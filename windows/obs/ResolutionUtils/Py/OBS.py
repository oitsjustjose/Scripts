from subprocess import Popen


def on_event(event):
    if event == obspython.OBS_FRONTEND_EVENT_SCRIPTING_SHUTDOWN:
        proc = Popen(
            r".\Desktop.bat",
            cwd=r"TODO:\obs\ResolutionUtils",
            shell=True,
        )
        _ = proc.communicate()


def script_load(settings):
    obspython.obs_frontend_add_event_callback(on_event)
    proc = Popen(
        r".\Recording.bat",
        cwd=r"TODO:\obs\ResolutionUtils",
        shell=True,
    )
    _ = proc.communicate()
