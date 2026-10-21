#!/usr/bin/env python3
"""Offline Herdr surface for composer tests; never contacts a Herdr server."""

import fcntl
import json
import os
from pathlib import Path
import re
import struct
import sys
import termios

path = Path(os.environ["HERDR_SUBMIT_TEST_STATE"])
state = json.loads(path.read_text())
args = sys.argv[1:]
state["calls"].append(args)


def reset_session():
    state["resets"] += 1
    state["composer"] = ""
    if not state.get("ignore_resets"):
        state.pop("probe_word", None)
    state["model"] = state.get("model_after_reset", state["model"])


def resize(cols):
    fd = os.open(f'/proc/{state["pid"]}/fd/0', os.O_RDONLY | os.O_NOCTTY)
    try:
        fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, cols, 0, 0))
    finally:
        os.close(fd)


def submit(text):
    state["submissions"].append(text)
    state["status"] = "working"
    if "The probe word for this conversation is" in text:
        state["probe_word"] = "PERIWINKLE"
        state["reply"] = "main PROBE_OK_5E1B"
    elif "If an earlier message" in text:
        tail = re.search(r"NONE immediately followed by (\S+)\.", text)[1]
        state["reply"] = state.get("probe_word", "NONE") + tail
    elif "Count slowly" in text:
        state["counting"] = True
        state["reply"] = "1\n2\n3"
    else:
        state["reply"] = "completed"


result = {}
if args[:2] == ["pane", "get"]:
    result = {"pane": {"agent": state["agent"], "agent_status": state["status"],
                       "tab_id": "offline-test-tab"}}
    # The helper observes activity; a short task then settles unseen at done.
    if state["status"] == "working" and state["submissions"] and not state.get("counting"):
        state["status"] = "done"
elif args[:2] == ["pane", "process-info"]:
    result = {"process_info": {
        "shell_pid": state["pid"] if state.get("shell_prompt") else state["pid"] + 1,
        "foreground_processes": [{"pid": state["pid"], "cmdline": "offline-fixture"}],
    }}
elif args[:2] == ["pane", "layout"]:
    result = {"layout": {"zoomed": state["zoomed"],
                         "focused_pane_id": state["zoom_pane"]}}
elif args[:2] == ["pane", "zoom"]:
    state["zoomed"] = args[-1] == "--on"
    state["zoom_pane"] = args[2] if state["zoomed"] else "w1:p1"
    resize(state["zoom_cols"] if state["zoomed"] and args[2] == "w1:p2"
           else state["initial_cols"])
elif args[:2] == ["pane", "send-text"]:
    state["composer"] = args[3]
elif args[:2] == ["pane", "send-keys"]:
    key = args[3]
    if key == "ctrl+u":
        state["composer"] = ""
    elif key == "ctrl+x":
        state["leader"] = True
    elif key == "n" and state.pop("leader", False):
        reset_session()
    elif key == "esc":
        if state.get("counting"):
            if state["agent"] != "opencode" or state.get("interrupt_armed"):
                state["counting"] = False
                state["status"] = "idle"
            else:
                state["interrupt_armed"] = True
        elif state["agent"] == "opencode" and state["composer"].startswith("/"):
            state["composer"] = ""
    elif key == "enter":
        text = state["composer"]
        if text == "/clear":
            reset_session()
        elif text:
            submit(text)
        state["composer"] = ""
elif args[:2] == ["pane", "read"]:
    if args[args.index("--source") + 1] == "visible":
        kind, model = state["agent"], state["model"]
        screen = {"cursor": f"→ Add a follow-up\n────\n{model}",
                  "codex": f"› Follow up\n\n{model}",
                  "opencode": f"┃\n┃ Build · {model} OpenAI · max"}
        print(screen.get(kind, "no supported composer"))
    else:
        print(state["composer"] or state.get("reply", ""))
elif args[:2] == ["pane", "wait-output"]:
    # Only the current completed reply matches, never the submitted prompt.
    reply = state.get("reply", "")
    if "--match" in args:
        matched = args[args.index("--match") + 1] in reply
    else:
        matched = re.search(args[args.index("--regex") + 1], reply)
    if not matched:
        path.write_text(json.dumps(state))
        sys.exit(1)
else:
    raise SystemExit(f"unexpected mock command: {args!r}")

path.write_text(json.dumps(state))
if args[:2] != ["pane", "read"]:
    print(json.dumps({"result": result}))
