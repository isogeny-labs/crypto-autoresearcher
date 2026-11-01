# EKS image preflight for the n51 D5 stream trial

The pinned EKS image accepted the native small-system D5 fixture, streamed its 1,040-byte candidate to the Job's assigned S3 prefix, read back the full object, and passed the original independent checker with codimension 3. A separate host readback of the candidate matched both the producer and in-pod readback SHA-256: `7cf2d46d96fe00dfddd1277935c7f0b6577c7ab9cbdc774151c81f56fee82d73`. This qualifies the image's transfer and checker path; the n51 result is a separate Job.

The control used image digest `sha256:67eea58f5d4a7a8882b55f089c6063bb49fad58d40260ee9b0ceb349fc0e4581`, 2 CPU, 2 GiB, a 900-second Job limit, and zero retries. Its immutable public bundle was 120,902 bytes with SHA-256 `3be9cffdf5fb0434a9c49a8e10f103fe21c07a990b5688cc3fdf9e2137bfc103`. The successful Job was `semaev-d5-stream-custody-preflight-public-v3-20261101`, UID `ef4cb600-5b65-4ead-ba22-38f87369270b`, pod UID `74fd9407-ebf3-4d3b-a68d-5c5ddee41da2`. Its S3 receipt, checker transcript, candidate and independent readback manifest are in [preflight](preflight/).

| Job | Outcome | Native fixture reached? |
| --- | --- | --- |
| `semaev-d5-stream-custody-preflight-20261101` | `HeadObject 403` on a separate artifact-store bucket | No |
| `semaev-d5-stream-custody-preflight-public-20261101` | Bootstrap lacked `/work/results` | No |
| `semaev-d5-stream-custody-preflight-public-v2-20261101` | Exact public bundle downloaded; image had no `tar` command | No |
| `semaev-d5-stream-custody-preflight-public-v3-20261101` | Qualified; full S3 readback and original checker accepted | Yes |

The diagram [preflight-pipeline.svg](preflight-pipeline.svg) shows where each attempt stopped. Only the fourth Job tested the native path. Its candidate and checker receipt are a transport control, not a degree-six bound for n51. The frontier Job uses the same image and a distinct frozen request and result prefix.
