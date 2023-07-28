# This file is part of ts_m2gui.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import shutil

import pytest


@pytest.mark.asyncio
async def close_process(process: asyncio.subprocess.Process) -> None:
    if process.returncode is None:
        process.terminate()
        await asyncio.wait_for(process.wait(), timeout=5.0)
    else:
        print("Warning: subprocess had already quit.")
        try:
            assert process.stderr is not None  # make mypy happy
            errbytes = await process.stderr.read()
            print("Subprocess stderr: ", errbytes.decode())
        except Exception as e:
            print(f"Could not read subprocess stderr: {e}")


@pytest.mark.asyncio
async def test_run_m2gui() -> None:
    # Make sure this application exists
    application_name = "run_m2gui"
    exe_path = shutil.which(application_name)

    assert exe_path is not None

    # Run the process and get the standard output
    process = await asyncio.create_subprocess_exec(
        application_name,
        "-h",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    assert process.stdout is not None  # make mypy happy
    stdout = await process.stdout.readline()

    # Close the process first before the assertion
    await close_process(process)

    # If there is the error, the result will be empty
    assert stdout.decode() != ""
