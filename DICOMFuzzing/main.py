import click
import yaml
import time
import os
from pathlib import Path

from network.scu import DicomSCU
from fuzzer.engine import FuzzingEngine
from utils.logger import setup_logger

@click.command()
@click.option('--target', required=False, help='Target IP address')
@click.option('--port', required=False, type=int, help='Target port')
@click.option('--config', default='config.yaml', help='Path to configuration file')
@click.option('--mode', default='fuzz', type=click.Choice(['test', 'fuzz', 'gui']), help='Operation mode')
def main(target, port, config, mode):
    """DICOM Fuzzing Tool CLI"""
    # If mode is GUI, we don't necessarily need target/port from CLI, simple defaults are fine.
    
    if mode == 'gui':
        from gui.app import main as run_gui
        run_gui()
        return

    logger = setup_logger()
    logger.info(f"Starting DICOM Fuzzing Tool in {mode} mode")
    logger.info(f"Target: {target}:{port}")
    
    # Load config
    if os.path.exists(config):
        with open(config, 'r') as f:
            cfg = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {config}")
    else:
        logger.warning(f"Config file {config} not found, using defaults")
        cfg = {}

    if mode == 'test':
        logger.info("Running connectivity test...")
        scu = DicomSCU(target, port, cfg.get('network', {}))
        if scu.echo():
            logger.info("Connection successful")
        else:
            logger.error("Connection failed")

    elif mode == 'fuzz':
        logger.info("Starting fuzzing session...")
        engine = FuzzingEngine(target, port, cfg)
        engine.run()

if __name__ == '__main__':
    main()
