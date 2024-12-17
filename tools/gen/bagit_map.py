import os
import shutil
import tarfile
import bagit
import logging
from pathlib import Path
from datetime import datetime
import time


#from config import CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BagitTransfer')


def pack_and_transfer(source_path: Path, transfer_dir: Path) -> None:
    """
    Pack files into a BagIt bag and transfer it.

    Args:
        source_path: Directory containing files to bag
        transfer_dir: Where to put the packed bag
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    bag_name = f"bag_{timestamp}"
    temp_bag_dir = Path(f"/tmp/{bag_name}")

    try:
        # Create bag
        logger.info(f"Creating bag from {source_path}")
        bagit.make_bag(
            temp_bag_dir,
            {
                "Source-Organization": "BagIt Transfer",
                "Bagging-Date": timestamp,
            }
        )

        # Copy files into bag's data directory
        for item in source_path.iterdir():
            if item.is_file():
                shutil.copy2(item, temp_bag_dir / "data")

        # Create tarball
        tar_path = transfer_dir / f"{bag_name}.tar"
        logger.info(f"Creating tarball at {tar_path}")
        with tarfile.open(tar_path, "w") as tar:
            tar.add(temp_bag_dir, arcname=bag_name)

        logger.info(f"Successfully transferred bag to {tar_path}")

    finally:
        # Cleanup
        if temp_bag_dir.exists():
            shutil.rmtree(temp_bag_dir)


def receive_and_unpack(transfer_dir: Path, destination_dir: Path) -> None:
    """
    Watch for new bags, unpack them when they arrive.

    Args:
        transfer_dir: Directory to watch for new bags
        destination_dir: Where to unpack the bags
    """
    processed = set()

    # Get initial list of processed files
    for file in transfer_dir.glob("*.tar"):
        processed.add(file.name)

    while True:
        # Look for new tar files
        for tar_path in transfer_dir.glob("*.tar"):
            if tar_path.name not in processed:
                logger.info(f"New bag found: {tar_path}")
                try:
                    # Unpack the tar file
                    with tarfile.open(tar_path) as tar:
                        tar.extractall(destination_dir)

                    bag_path = destination_dir / tar_path.stem

                    # Verify the bag
                    bag = bagit.Bag(bag_path)
                    if bag.is_valid():
                        logger.info(f"Successfully unpacked and verified {tar_path}")
                        processed.add(tar_path.name)
                    else:
                        logger.error(f"Bag validation failed for {tar_path}")

                except Exception as e:
                    logger.error(f"Error processing {tar_path}: {e}")

        time.sleep(1)  # Wait before checking again


if __name__ == "__main__":
    import sys

    # if len(sys.argv) < 2:
    #     print("Usage: script.py [pack|receive] [source_dir] [transfer_dir]")
    #     sys.exit(1)
    sys.argv.pop()
    mode = "pack" if not sys.argv else sys.argv[0]
    #CONF = CONFIG.ROOT_PATH / "data"
    # todo ...
    # print(CONF.absolute().as_posix())
    # if mode == "pack":
    #     if len(sys.argv) != 4:
    #         print("Usage: script.py pack source_dir transfer_dir")
    #         sys.exit(1)
    #     source_dir = CONF / "bags3source"
    #     transfer_dir= CONF / "bags3transfer"
    #
    #     pack_and_transfer(source_dir, transfer_dir)
    #
    # elif mode == "receive":
    #     if len(sys.argv) != 4:
    #         print("Usage: script.py receive transfer_dir destination_dir")
    #         sys.exit(1)
    #     transfer_dir = Path(sys.argv[2])
    #     destination_dir = Path(sys.argv[3])
    #     receive_and_unpack(transfer_dir, destination_dir)


    # pack_and_transfer(source_dir, transfer_dir)