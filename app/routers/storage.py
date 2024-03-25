from typing import Annotated
from datetime import datetime
from typing import List

from fastapi import APIRouter, UploadFile, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from app.schemas.file import FileOut, DirectoryOut
from app.models.file import File, Directory
from app.models.user import User
from app.config import settings
from app.storage import iter_chunks
from app.oauth2 import get_current_user
from app.utils import get_filename

router = APIRouter(prefix="/files", tags=["Storage"])

@router.post("/{directory}", response_model=DirectoryOut, status_code=status.HTTP_201_CREATED)
async def create_directory(
        directory: str,
        current_user: User = Depends(get_current_user)
):
    if not directory:
        raise HTTPException(status_code=400, detail="Le nom du dossier est requis")

    # Recherchez le dossier dans la base de données
    existing_dir = Directory.objects(dir_name=directory, owner_id=current_user.id).first()

    # Si le dossier existe déjà, lèvez une exception
    if existing_dir:
        raise HTTPException(status_code=409, detail="Le dossier existe déjà")

    # Créez le dossier s'il n'existe pas déjà
    new_dir = Directory(dir_name=directory, owner_id=current_user.id,owner=current_user.name)
    new_dir.save()

    # created_directory = DirectoryOut(
    #     dir_name=new_dir.dir_name,
    #     owner=current_user.name,
    #     created_at=new_dir.created_at
    # )

    return new_dir


@router.get("/directories", response_model=list[DirectoryOut])
async def get_user_directories(
        current_user: User = Depends(get_current_user)
):
    return Directory.objects()


@router.post("/upload/{directory}", response_model=FileOut, status_code=status.HTTP_201_CREATED)
async def upload_file(directory: str,
                      file: UploadFile,
                      current_user: Annotated[User, Depends(get_current_user)],
                      filename: str | None = None, keep: bool = True):
    filename = filename or file.filename

    if '.' not in filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid filename ({filename}).must contains an "
                                   f"extension correctly set the Content-Type")

    found_dir = Directory.objects(dir_name=directory).first()
    if found_dir is None:
        found_dir = Directory(dir_name=directory, owner_id=current_user.id,owner=current_user.name)
        found_dir.save()

    found_file: File = File.objects(file_name=filename, parent=found_dir).first()
    if found_file is not None:
        if keep:
            filename = get_filename(filename)
        else:
            found_file.delete()

    new_file = File(file_name=filename, content_type=file.content_type,
                    owner_id=current_user.id,owner=current_user.name, parent=found_dir)

    new_file.file_content.new_file()
    new_file.file_content.write(file.file.read())
    new_file.file_content.close()

    new_file.save()

    # return FileOut(file_id=new_file.file_id, file_name=new_file.file_name, content_type=new_file.content_type,
    #                owner_id=new_file.owner_id, owner=current_user)

    return new_file


@router.get("/download/{directory}/{filename}")
async def dowload_file(directory: str,
                       filename: str,
                       _current_user: Annotated[User, Depends(get_current_user)]):
    found_dir = Directory.objects(dir_name=directory).first()
    if found_dir is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Directoy {directory} does not exists")

    file: File = File.objects(file_name=filename, parent=found_dir).first()

    if file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'File with id {filename} does not exists in {directory} directory ')

    return StreamingResponse(content=iter_chunks(file.file_content, settings.chunk_size),
                             media_type=file.content_type)


# @router.get("", response_model=list[FileOut])
# async def get_all_files(_current_user: Annotated[User, Depends(get_current_user)],
#                         limit: int = 10, skip: int = 0):
#     return File.objects().limit(limit).skip(skip)


@router.get("", response_model=list[FileOut])
async def get_files_in_directory(current_user: Annotated[User, Depends(get_current_user)],
                                 directory: str | None = None,
                                 limit: int = 5,
                                 skip: int = 0
                                 ):
    if directory is None:
        query = File.objects()
    else:
        found_dir = Directory.objects(dir_name=directory).first()
        if found_dir is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Directoy {directory} does not exists")
        query = File.objects(parent=found_dir)

    return query.limit(limit).skip(skip)


@router.delete("/{directory}/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(directory: str,
                      filename: str,
                      current_user: Annotated[User, Depends(get_current_user)]
                      ):
    found_dir = Directory.objects(dir_name=directory).first()
    if found_dir is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Directoy {directory} does not exists")

    file: File = File.objects(file_name=filename, parent=found_dir).first()

    if file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'File {filename} does not exists '
                                   f'in {directory} directory')

    if file.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to delete {directory}/{filename}")

    file.file_content.delete()
    file.delete()


