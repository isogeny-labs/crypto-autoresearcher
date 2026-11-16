# Proposed second journal reconciliation

No canonical journal has changed. The previous authorization was one-time; this proposed operation requires a new explicit owner exception.

Latest main `5f362bfc48e9f3546f33cc0c43e5d3dc8f4fc2ba` has 84 entries; the preserved continuation `84c4973195ea83b39d42e8fa6c5f2c53588dbcc7` has 96, with a shared prefix of 76. The external native preview keeps every main byte and appends 19 unchanged unsigned claim registrations plus one provenance note: 104 entries. All19 standing objects remain identical; keyrings are identical: True.

The preview SHA256 is `4db61474764793601dbf8c1441a24d8944e172ba06470c9b66bf889316f2a523`. The compressed originals and preview round-trip exactly; native chain/prefix checks pass. The preview is not an application receipt and its events will not be reused. `checks.json` contains exact inputs, digests, standings and registry-conflict analysis.

Schema-registry existing-entry collisions: 0. No existing registry record or pin may be changed to make a merge succeed. Other derived progress files may be regenerated and catalog entries retained. Original PR2590 remains unchanged. No scientific run, standing promotion or budget change is authorized by this proposal.
