*This project has been created as part of the 42 curriculum by omischle.*

# NetPractice

## Description

NetPractice is an introductory networking project from the 42 curriculum. The goal
is to solve a series of small-scale network configuration problems in order to
discover how TCP/IP addressing works in practice. Each level presents a
non-functioning network diagram (hosts, switches, routers, interfaces) that must
be repaired by setting correct IP addresses, subnet masks and routing entries so
that the requested communication between machines succeeds.

The project contains 10 levels of increasing difficulty, covering subnetting,
default gateways, routing tables and the distinction between hosts inside the
same network and hosts reached through a router.

## Instructions

The training interface is delivered as a local web application.

1. Download the archive attached to the project page on the intranet and extract
   it into any folder.
2. From that folder, run the provided launcher:
   ```
   ./run.sh
   ```
   This starts a local web server and opens the NetPractice page in your
   browser. If `run.sh` does not work on your machine, you can start the server
   manually:
   ```
   python3 -m http.server 49242
   ```
   Then open `http://localhost:49242` in your browser.
3. Enter your intranet **login** in the field on the welcome page before
   starting (the configuration is generated from it, and the evaluator uses the
   same login to verify your answers).
4. For each level, edit the unshaded fields of the diagram and click **Check
   again** until the status turns OK. Click **Get my config** to export the
   level as a JSON file, then move it to the root of this repository under the
   name `levelX.json` (where `X` is the level number).

### Submission

The repository must contain, at its root:

- `README.md` (this file).
- The 10 exported configuration files, one per level:
  `level1.json`, `level2.json`, ..., `level10.json`.

During the defense, three random levels must be solved live within a limited
time, without any external tool (a basic calculator such as `bc` is tolerated).

## Resources

Networking concepts used and studied throughout this project:

- **TCP/IP addressing** — IPv4 addresses, network vs host portion.
- **Subnet masks** — CIDR notation, computing network/broadcast addresses and
  the range of usable hosts.
- **Default gateways** — how a host reaches destinations outside its own
  subnet.
- **Routers and switches** — the role of each device, and the difference
  between layer-2 forwarding (switch) and layer-3 routing (router).
- **Routing tables** — destination/next-hop entries and the `0.0.0.0/0`
  default route.
- **OSI layers** — situating addressing and routing within the OSI model.

Useful references:

- RFC 791 (Internet Protocol) and RFC 950 (subnetting).
- Cisco "IP Addressing and Subnetting for New Users".
- Subnetting cheat sheets and CIDR/VLSM tutorials.

### Use of AI

AI assistants were used as a study and review aid only:

- To explain TCP/IP concepts (subnet masks, CIDR, default routes) and to clarify
  the failure messages produced by the NetPractice logs.
- To double-check the reasoning behind a chosen address/mask before validating a
  level in the interface.
- To help draft and proofread this `README.md`.

AI was **not** used to solve the levels in place of understanding them: every
configuration submitted in this repository was reasoned through and verified by
hand in the training interface, so that the same kind of problems can be solved
live during the defense without external tools.
