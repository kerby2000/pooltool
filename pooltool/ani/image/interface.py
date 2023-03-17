from typing import Any, List, Protocol, Tuple

import numpy as np
from numpy.typing import NDArray
from panda3d.core import GraphicsOutput, Texture

from pooltool.ani.animate import FrameStepper
from pooltool.ani.camera import CameraState, cam, camera_states
from pooltool.ani.globals import Global
from pooltool.ani.hud import HUDElement, hud
from pooltool.ani.image.utils import rgb2gray
from pooltool.system.datatypes import System

DEFAULT_CAMERA = camera_states["7_foot_offcenter"]


class Exporter(Protocol):
    def save(self, data: NDArray[np.uint8]) -> Any:
        ...


def image_stack(
    system: System,
    interface: FrameStepper,
    size: Tuple[int, int] = (230, 144),
    fps: float = 30.0,
    camera_state: CameraState = DEFAULT_CAMERA,
    gray: bool = False,
    show_hud: bool = False,
) -> NDArray[np.uint8]:
    """Return the shot's rendered frames as a numpy array stack

    Args:
        camera_state:
            A camera state specifying the camera's view of the table.
        gray:
            If True, the image is saved in grayscale.
        show_hud:
            If True, the HUD will appear in the images.

    Returns:
        A numpy array of size (N, x, y), where N is the number of frames, and x & y are
        the frame dimensions (in pixels).
    """
    iterator, frames = interface.iterator(system, size, fps)

    # Clear all existing image textures, then create a new one
    tex = Texture()
    Global.base.win.clearRenderTextures()
    Global.base.win.addRenderTexture(
        tex, GraphicsOutput.RTMCopyRam, GraphicsOutput.RTPColor
    )

    if show_hud:
        hud.init()
        hud.elements[HUDElement.help_text].help_hint.hide()
        hud.update_cue(system.cue)
    else:
        hud.destroy()

    cam.load_state(camera_state)

    # Initialize a numpy array image stack
    x, y = size
    imgs: List[NDArray[np.uint8]] = []

    for frame in range(frames):
        next(iterator)
        img = image_array_from_texture(tex)

        if gray:
            img = rgb2gray(img)

        imgs.append(img)

    return np.array(imgs, dtype=np.uint8)


def save_images(self, exporter: Exporter, *args, **kwargs) -> None:
    exporter.save(image_stack(*args, **kwargs))


def image_array_from_texture(tex: Texture) -> NDArray[np.uint8]:
    assert tex.hasRamImage()

    array = np.copy(np.frombuffer(tex.getRamImage(), dtype=np.uint8))
    array.shape = (
        tex.getYSize(),
        tex.getXSize(),
        tex.getNumComponents(),
    )

    # This flips things rightside up and orders RGB correctly
    return array[::-1, :, ::-1]
