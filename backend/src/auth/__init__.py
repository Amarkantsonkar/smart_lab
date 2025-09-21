from fastapi.security import OAuth2PasswordBearer

# Import dependencies
from .route_dependencies import oauth2_scheme, get_current_user, require_role