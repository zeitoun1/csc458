# Programming Assignment 0 Writeup

**Name:** Ali Zeitoun

**UTORid:** zeitoun4

**People/resources credited:** python docs

**Approximate time spent:** 1 hour

## Mandatory questions

1. In an HTTP/1.1 request, what byte sequence separates one header line from the next, and what marks the end of the complete header block?

   The sequence of \r\n (CRLF) separates one header line from the next, and the end of a complete header block is marked by 2 CRLFs so \r\n\r\n.

2. Why must `get_url()` keep calling `recv()` until it returns `b""` instead of making exactly one `recv()` call?

   TCP cockets use a byte stream, thus recv might return before all data arrives to socket. So we have to keep on calling recv until we read an empty byte b'' which means connection has closed, so no more data left.

3. What does the `Connection: close` request header accomplish in this assignment? How does it help the client know that the response is complete?

   It makes the server close the connection after sending a response, this helps client know response is complete since recv will read an empty byte b'' when the connection is closed.

4. In Python, why does the starter program write the response with `sys.stdout.buffer.write(...)` instead of decoding every response as UTF-8 text first?

   Since HTTP bodies are not guaranteed to be UTF-8 text.

## Optional feedback

- I think this assignment could be improved by: providing a repo instead of having to download the files

