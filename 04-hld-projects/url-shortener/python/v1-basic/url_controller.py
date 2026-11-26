"""
URL Shortener - V1 Basic

HTTP Controller/Handler layer for URL shortening API.
Framework-agnostic implementation.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

# Import from service module (would be: from url_shortening_service import ...)
# For skeleton, assuming these are available in the same context


@dataclass
class HttpRequest:
    """HTTP Request abstraction."""
    method: str
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Dict[str, Any] = field(default_factory=dict)
    path_params: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, str] = field(default_factory=dict)
    
    def get_path_param(self, name: str) -> Optional[str]:
        return self.path_params.get(name)
    
    def get_query_param(self, name: str) -> Optional[str]:
        return self.query_params.get(name)
    
    def get_body_field(self, name: str) -> Any:
        return self.body.get(name)


@dataclass
class HttpResponse:
    """HTTP Response abstraction."""
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    
    @staticmethod
    def ok(body: Any) -> 'HttpResponse':
        return HttpResponse(status_code=200, body=body)
    
    @staticmethod
    def created(body: Any) -> 'HttpResponse':
        return HttpResponse(status_code=201, body=body)
    
    @staticmethod
    def redirect(location: str, permanent: bool = True) -> 'HttpResponse':
        status = 301 if permanent else 302
        return HttpResponse(
            status_code=status,
            headers={"Location": location}
        )
    
    @staticmethod
    def not_found(message: str) -> 'HttpResponse':
        return HttpResponse(status_code=404, body={"error": message})
    
    @staticmethod
    def conflict(message: str) -> 'HttpResponse':
        return HttpResponse(status_code=409, body={"error": message})
    
    @staticmethod
    def bad_request(message: str) -> 'HttpResponse':
        return HttpResponse(status_code=400, body={"error": message})
    
    @staticmethod
    def gone(message: str) -> 'HttpResponse':
        return HttpResponse(status_code=410, body={"error": message})
    
    @staticmethod
    def no_content() -> 'HttpResponse':
        return HttpResponse(status_code=204)


class UrlController:
    """
    URL Controller handling HTTP requests.
    
    Routes:
        POST /api/v1/urls              - Create short URL
        GET  /{shortCode}              - Redirect to original URL
        GET  /api/v1/urls/{code}/stats - Get URL statistics
        DELETE /api/v1/urls/{code}     - Delete URL
    """
    
    def __init__(self, url_service):
        """
        Initialize controller with URL service.
        
        Args:
            url_service: Instance of UrlShorteningService
        """
        self._url_service = url_service
    
    def create_short_url(self, request: HttpRequest) -> HttpResponse:
        """
        POST /api/v1/urls
        Create a new short URL.
        """
        try:
            long_url = request.get_body_field("longUrl")
            custom_alias = request.get_body_field("customAlias")
            expires_at_str = request.get_body_field("expiresAt")
            
            if not long_url:
                return HttpResponse.bad_request("longUrl is required")
            
            expires_at = None
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            
            # Create request DTO
            from url_shortening_service import CreateUrlRequest
            create_request = CreateUrlRequest(
                long_url=long_url,
                custom_alias=custom_alias,
                expires_at=expires_at
            )
            
            response = self._url_service.create_short_url(create_request)
            
            return HttpResponse.created({
                "shortUrl": response.short_url,
                "shortCode": response.short_code,
                "longUrl": response.long_url,
                "createdAt": response.created_at.isoformat(),
                "expiresAt": response.expires_at.isoformat() if response.expires_at else None
            })
            
        except AliasAlreadyExistsError as e:
            return HttpResponse.conflict(str(e))
        except ValueError as e:
            return HttpResponse.bad_request(str(e))
        except Exception as e:
            return HttpResponse.bad_request(f"Error: {str(e)}")
    
    def redirect(self, request: HttpRequest) -> HttpResponse:
        """
        GET /{shortCode}
        Redirect to the original URL.
        """
        short_code = request.get_path_param("shortCode")
        
        if not short_code:
            return HttpResponse.bad_request("Short code is required")
        
        try:
            original_url = self._url_service.get_original_url(short_code)
            
            if not original_url:
                return HttpResponse.not_found(f"URL not found: {short_code}")
            
            return HttpResponse.redirect(original_url)
            
        except UrlExpiredError as e:
            return HttpResponse.gone(str(e))
    
    def get_stats(self, request: HttpRequest) -> HttpResponse:
        """
        GET /api/v1/urls/{shortCode}/stats
        Get URL statistics.
        """
        short_code = request.get_path_param("shortCode")
        
        stats = self._url_service.get_stats(short_code)
        
        if not stats:
            return HttpResponse.not_found(f"URL not found: {short_code}")
        
        return HttpResponse.ok({
            "shortCode": stats.short_code,
            "longUrl": stats.long_url,
            "clicks": stats.click_count,
            "createdAt": stats.created_at.isoformat(),
            "expiresAt": stats.expires_at.isoformat() if stats.expires_at else None
        })
    
    def delete_url(self, request: HttpRequest) -> HttpResponse:
        """
        DELETE /api/v1/urls/{shortCode}
        Delete a short URL.
        """
        short_code = request.get_path_param("shortCode")
        
        deleted = self._url_service.delete_url(short_code)
        
        if not deleted:
            return HttpResponse.not_found(f"URL not found: {short_code}")
        
        return HttpResponse.no_content()


# Exception imports for reference (normally imported from service module)
class AliasAlreadyExistsError(Exception):
    pass

class UrlExpiredError(Exception):
    pass
