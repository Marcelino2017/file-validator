from fastapi import APIRouter, Depends, HTTPException, status

from app.application.auth_service import LoginInput, LoginUser, RegisterUser, RegisterUserInput
from app.application.exceptions import ConflictError, UnauthorizedError, ValidationError
from app.domain.entities import User
from app.interfaces.dependencies import (
    get_current_user,
    get_login_user_use_case,
    get_register_user_use_case,
)
from app.interfaces.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    use_case: RegisterUser = Depends(get_register_user_use_case),
) -> UserResponse:
    try:
        created_user = use_case.execute(
            RegisterUserInput(
                first_name=request.first_name,
                last_name=request.last_name,
                cedula=request.cedula,
                enterprise_name=request.enterprise_name,
                nit=request.nit,
                password=request.password,
            )
        )
    except (ConflictError, ValidationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return UserResponse(
        id=created_user.id or 0,
        first_name=created_user.first_name,
        last_name=created_user.last_name,
        cedula=created_user.cedula,
        enterprise_id=created_user.enterprise_id,
    )


@router.post("/login", response_model=AuthResponse)
def login(
    request: LoginRequest,
    use_case: LoginUser = Depends(get_login_user_use_case),
) -> AuthResponse:
    try:
        result = use_case.execute(LoginInput(cedula=request.cedula, password=request.password))
    except UnauthorizedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    return AuthResponse(
        access_token=result.access_token,
        token_type=result.token_type,
        user_id=result.user_id,
        cedula=result.cedula,
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id or 0,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        cedula=current_user.cedula,
        enterprise_id=current_user.enterprise_id,
    )
