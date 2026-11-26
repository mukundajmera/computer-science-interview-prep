import hashlib
import hmac
import time
import uuid
from typing import Dict, List, Optional


class ObjectMetadata:
    def __init__(self, key: str, version_id: str, data: Optional[bytes], is_deleted: bool, etag: Optional[str]):
        self.key = key
        self.version_id = version_id
        self.data = data
        self.size = len(data) if data is not None else 0
        self.is_deleted = is_deleted
        self.last_modified = time.time()
        self.etag = etag


class Bucket:
    def __init__(self, name: str):
        self.name = name
        self.objects: Dict[str, List[ObjectMetadata]] = {}  # key -> list of versions


class S3StorageService:
    def __init__(self):
        self.buckets: Dict[str, Bucket] = {}
        self.secret_access_key = b"test-secret-key"
        self.used_signatures = set()

    def create_bucket(self, bucket_name: str) -> None:
        if bucket_name not in self.buckets:
            self.buckets[bucket_name] = Bucket(bucket_name)

    def delete_bucket(self, bucket_name: str) -> None:
        if bucket_name in self.buckets:
            del self.buckets[bucket_name]

    def _generate_version_id(self) -> str:
        return str(uuid.uuid4())

    def _calculate_md5_etag(self, data: Optional[bytes]) -> Optional[str]:
        if data is None:
            return None
        return hashlib.md5(data).hexdigest()

    def put_object(self, bucket_name: str, key: str, data: bytes) -> str:
        if bucket_name not in self.buckets:
            raise ValueError("Bucket not found")
        
        bucket = self.buckets[bucket_name]
        version_id = self._generate_version_id()
        etag = self._calculate_md5_etag(data)
        
        obj = ObjectMetadata(key, version_id, data, False, etag)
        
        if key not in bucket.objects:
            bucket.objects[key] = []
        bucket.objects[key].append(obj)
        
        return version_id

    def get_object(self, bucket_name: str, key: str, version_id: Optional[str] = None) -> bytes:
        return self.get_object_with_range(bucket_name, key, version_id, -1, -1)

    def get_object_with_range(self, bucket_name: str, key: str, version_id: Optional[str] = None, start: int = -1, end: int = -1) -> bytes:
        if bucket_name not in self.buckets:
            raise ValueError("Bucket not found")
            
        bucket = self.buckets[bucket_name]
        if key not in bucket.objects or not bucket.objects[key]:
            raise ValueError("Object not found")
            
        versions = bucket.objects[key]
        obj = None
        
        if version_id is None:
            obj = versions[-1]
        else:
            for v in versions:
                if v.version_id == version_id:
                    obj = v
                    break
                    
        if obj is None or obj.is_deleted:
            raise ValueError("Object not found or deleted")
            
        if start < 0 and end < 0:
            return obj.data

        data_len = len(obj.data)
        s = max(0, start)
        e = data_len - 1 if end < 0 else min(data_len - 1, end)
        
        if s > e or s >= data_len:
            raise ValueError("Invalid byte range")
            
        return obj.data[s:e+1]

    def delete_object(self, bucket_name: str, key: str, version_id: Optional[str] = None) -> str:
        if bucket_name not in self.buckets:
            raise ValueError("Bucket not found")
            
        bucket = self.buckets[bucket_name]
        
        if version_id is None:
            # Soft delete: add a delete marker
            delete_version_id = self._generate_version_id()
            delete_marker = ObjectMetadata(key, delete_version_id, None, True, None)
            
            if key not in bucket.objects:
                bucket.objects[key] = []
            bucket.objects[key].append(delete_marker)
            
            return delete_version_id
        else:
            # Hard delete: remove the specific version
            if key in bucket.objects:
                bucket.objects[key] = [v for v in bucket.objects[key] if v.version_id != version_id]
                if not bucket.objects[key]:
                    del bucket.objects[key]
            return version_id

    def put_object_internal(self, bucket_name: str, key: str, data: bytes, etag: str) -> None:
        """Internal use for testing multipart upload results."""
        if bucket_name not in self.buckets:
            raise ValueError("Bucket not found")
            
        bucket = self.buckets[bucket_name]
        version_id = self._generate_version_id()
        obj = ObjectMetadata(key, version_id, data, False, etag)
        
        if key not in bucket.objects:
            bucket.objects[key] = []
        bucket.objects[key].append(obj)

    def generate_presigned_url(self, bucket_name: str, key: str, http_method: str, expiry_millis: int) -> str:
        # Note: This is an educational implementation and is not AWS SigV4 compatible. 
        # It does not provide a production security guarantee.
        base_path = f"https://{bucket_name}.s3.amazonaws.com/{key}"
        canonical_request = f"{http_method}\n{base_path}\n{expiry_millis}"
        signature = self._generate_signature(canonical_request, self.secret_access_key)
        
        return f"{base_path}?expires={expiry_millis}&signature={signature}"
        
    def verify_presigned_url(self, url: str, http_method: str, current_time_millis: int) -> bool:
        # Note: This is an educational implementation and is not AWS SigV4 compatible. 
        # It does not provide a production security guarantee.
        try:
            if "?" not in url:
                return False
                
            base_path, qs = url.split("?", 1)
            params = dict(p.split("=") for p in qs.split("&") if "=" in p)
            
            expires = int(params.get("expires", 0))
            signature = params.get("signature")
            
            if not signature or expires == 0:
                return False
                
            if current_time_millis > expires:
                return False
                
            if signature in self.used_signatures:
                return False  # Replay attack
                
            canonical_request = f"{http_method}\n{base_path}\n{expires}"
            expected_signature = self._generate_signature(canonical_request, self.secret_access_key)
            
            is_valid = hmac.compare_digest(expected_signature, signature)
            if is_valid:
                self.used_signatures.add(signature)
            return is_valid
        except Exception:
            return False

    def _generate_signature(self, data: str, secret: bytes) -> str:
        return hmac.new(secret, data.encode('utf-8'), hashlib.sha256).hexdigest()
