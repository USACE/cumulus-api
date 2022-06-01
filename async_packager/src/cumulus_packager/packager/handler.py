"""_summary_
"""

# import os
# from collections import namedtuple

# from cumulus_packager.configurations import WRITE_TO_BUCKET
# from cumulus_packager import logger
# from cumulus_packager.packager import package_status
# from cumulus_packager.writers import pkg_writer

# this = os.path.basename(__file__)

# def package(callback=None, req):


#     # Get needed information from info
#     id = info["download_id"]
#     output_key = info["output_key"]
#     contents = info["contents"]
#     extent = info["extent"]
#     format = info["format"]

#     # If no files are present, notify database of failure and return from function
#     filecount = len(contents)
#     if filecount == 0:
#         packager_update_fn(id, STATUS["FAILED"], 0, None)

#         return json.dumps({"failure": "no files to process", "filecount": filecount})

#     # If output format writer not implemented
#     writer = get_writer(format)
#     if writer is None:
#         logger.info("Setting STATUS to FAILED")
#         packager_update_fn(id, STATUS["FAILED"], 0, None)
#         return json.dumps(
#             {
#                 "failure": f"writer not implemented for format {format}",
#                 "filecount": None,
#             }
#         )

#     # I tried to avoid a callback function, but it's the best option among others
#     # This allows us to move all code concerned with packaging a DSS file into a separate file
#     # without:
#     #   1. Putting imports or implementation details about a status update in the file that
#     #      should only be concerned with DSS packaging.
#     #   2. Calling dss.Open() inside of a for loop, adding file open/close overhead on each
#     #      write.
#     #  With this approach, the write_record_to_dssfile() method knows nothing more than that it
#     #  has a function it needs to call with the iteration counter every time it adds a record to
#     #  a dss file
#     def callbackFn(idx):
#         """Notify the Cumulus API of status/progress"""
#         progress = int((int(idx + 1) / int(filecount)) * 100)

#         if progress < 100:
#             status_id = STATUS["INITIATED"]
#         else:
#             status_id = STATUS["SUCCESS"]

#         packager_update_fn(id, status_id, progress)
#         return

#     # Get product count from event contents
#     with tempfile.TemporaryDirectory() as td:
#         outfile = writer(
#             os.path.join(td, os.path.basename(output_key)), extent, contents, callbackFn
#         )

#         # Upload the final output file to S3
#         if CONFIG.CUMULUS_MOCK_S3_UPLOAD:
#             # Mock good upload to S3
#             upload_success = True
#             # Copy file to output directory in the container
#             # shutil.copy2 will overwrite a file if it already exists.
#             shutil.copy2(outfile, "/output/" + os.path.basename(outfile))
#         else:
#             upload_success = upload_file(outfile, output_key)

#         # Call Packager Update Function one last time to add file key to database
#         if upload_success:
#             packager_update_fn(id, STATUS["SUCCESS"], 100, output_key)
#         else:
#             # Failed
#             packager_update_fn(id, STATUS["FAILED"], 100)

#     return json.dumps(
#         {
#             "success": "SOMETHING",
#         }
#     )


# def handle_message(payload_resp, dst):
#     """Converts JSON-Formatted message string to dictionary and calls package()"""
#     result = pkg_writer(
#         plugin=payload_resp.format,
#         id=payload_resp.download_id,
#         outkey=payload_resp.output_key,
#         extent=payload_resp.extent,
#         src=payload_resp.contents,
#         dst=dst,
#         cellsize=2000,
#         dst_srs="EPSG:5070",
#         callback=package_status,
#     )
#     return result
