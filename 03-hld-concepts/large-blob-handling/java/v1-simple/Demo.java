public class Demo {
    public static void main(String[] args) {
        ChunkedBlobUploader uploader = new ChunkedBlobUploader();

        byte[] chunk1 = "Hello, ".getBytes();
        byte[] chunk2 = "World!".getBytes();
        byte[] fullData = "Hello, World!".getBytes();

        String expectedSha256 = ChunkedBlobUploader.computeSha256(fullData);

        String sessionId = uploader.initiateSession("blob-123", 2, fullData.length, expectedSha256);
        System.out.println("Started session: " + sessionId);

        uploader.uploadChunk(sessionId, 0, chunk1);
        System.out.println("Uploaded chunk 0");

        System.out.println("Missing chunks: " + uploader.getMissingChunks(sessionId));

        uploader.uploadChunk(sessionId, 1, chunk2);
        System.out.println("Uploaded chunk 1");

        boolean complete = uploader.completeSession(sessionId);
        System.out.println("Session completed successfully: " + complete);

        byte[] blob = uploader.getBlob("blob-123");
        System.out.println("Retrieved blob: " + new String(blob));
    }
}
