"""BasinComps CLI wrapper"""
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BasinCompsRunner:
    """Executes BasinComps command-line utility"""

    def run_basincomps(
        self,
        tin_dir: Path,
        basin_file: Path,
        output_dir: Path,
        start_time: datetime,
        end_time: datetime,
        output_format: str = 'csv',
        use_metric: bool = True
    ) -> Dict[str, Any]:
        """
        Run BasinComps utility

        Args:
            tin_dir: Directory containing TIFF/TIN files
            basin_file: Shapefile with basin polygons
            output_dir: Output directory
            start_time: Start time
            end_time: End time
            output_format: Output format (csv, tabular, dss)
            use_metric: Use metric units

        Returns:
            Dictionary with output paths
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build command - use shell to find BasinComps in PATH
        import shutil
        basincomps_path = shutil.which('BasinComps')
        if not basincomps_path:
            raise RuntimeError("BasinComps executable not found in PATH")

        cmd = [basincomps_path]

        # TIN files (all TIFFs in directory)
        # Pass each file individually to avoid shell wildcard expansion issues
        import glob
        tif_files = sorted(glob.glob(str(tin_dir / '*.tif')))
        if not tif_files:
            raise ValueError(f"No TIF files found in {tin_dir}")

        # Add each file with its own -tinFile argument
        for tif_file in tif_files:
            cmd.extend(['-tinFile', tif_file])

        # Basin shapefile
        cmd.extend(['-basinFile', str(basin_file)])

        # Time range
        cmd.extend([
            '-sTime', start_time.strftime('%d%b%Y,%H%M').upper(),
            '-eTime', end_time.strftime('%d%b%Y,%H%M').upper()
        ])

        # Output files
        text_output = None
        dss_output = None

        if output_format in ['csv', 'tabular', 'csv_alt1']:
            text_output = output_dir / f'basincomps_output.{output_format}'
            cmd.extend([
                '-textOutFile', str(text_output),
                '-outputFormat', output_format
            ])

        # Always create DSS output
        dss_output = output_dir / 'basincomps_output.dss'
        cmd.extend(['-dssOutFile', str(dss_output)])

        # Options
        if use_metric:
            cmd.append('-SI')

        cmd.append('-gridCell')
        cmd.extend(['-saveType', 'total'])

        # Execute with shell
        # Build command string with proper quoting
        def quote_arg(arg):
            arg_str = str(arg)
            if ' ' in arg_str:
                # Paths with spaces need double quotes
                return f'"{arg_str}"'
            else:
                return arg_str

        cmd_str = ' '.join(quote_arg(arg) for arg in cmd)
        logger.info(f"Executing BasinComps with {len(tif_files)} TIF files")

        # Pass environment explicitly to ensure METVUE_EXE is available
        import os as os_module
        env = os_module.environ.copy()

        result = subprocess.run(
            cmd_str,
            shell=True,
            executable='/bin/bash',
            capture_output=True,
            text=True,
            cwd=output_dir,
            env=env
        )

        if result.returncode != 0:
            logger.error(f"BasinComps stderr: {result.stderr}")
            raise RuntimeError(f"BasinComps failed: {result.stderr}")

        logger.info(f"BasinComps completed successfully")
        logger.info(f"BasinComps stdout: {result.stdout}")
        logger.info(f"BasinComps stderr: {result.stderr}")

        return {
            'text_output': str(text_output) if text_output and text_output.exists() else None,
            'dss_output': str(dss_output) if dss_output and dss_output.exists() else None,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
