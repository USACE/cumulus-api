"""_summary_"""


import datetime
import os
import subprocess

from netCDF4 import Dataset


def wrf2cog(infile, outdir, varName):
    """Takes an infile to process and path to a directory where output files should be saved
    Returns array of objects [{ "filetype": "nohrsc_snodas_swe", "file": "file.tif", ... }, {}, ]
    """

    # logger.info(
    #     "****************************** WRF Columbia **********************************"
    # )

    startTime = datetime.datetime.now()

    # import pdb; pdb.set_trace()

    ncDataset = Dataset(infile)
    hour_array = ncDataset.variables["time"][:]
    ncDataset.close()

    strProjLccSphere = '-a_srs "+proj=lcc +lat_1=45 +lat_2=45 +lon_0=-120 +lat_0=45.80369 +x_0=0 +y_0=0 +a=6370000 +b=6370000 +units=m"'
    strNcExtent = "-a_ullr -341997.806, 816645.371, 858002.194, -539354.629"
    strFinalExtent = "-projwin -337997.806, 812645.371, 854002.194, -535354.629"

    intBand = 0
    outfile_list = []
    dtVersion = datetime.datetime.strptime("2021_03_06", "%Y_%m_%d")

    for theHour in hour_array:
        # We want to round to an integer to make sure that we are using an exact hour.
        # For some reason round on a numpy.float32 is not giving an integer in the cumulus-api_geoprocess python instance (3.8.5)
        # The Python standard float is double
        # So convert numpy.float32 to float and round that.

        intHour = round(float(theHour))
        currentPDate = datetime.datetime(1850, 1, 1, 0) + datetime.timedelta(
            hours=intHour
        )
        intBand += 1  # They start at 1 for gdal_translate command

        # test with 2 bands
        # if intBand < 2490 or intBand > 2491:
        #     continue

        strDateFormat = "%Y_%m_%d_T%H_%M"
        strCurrentDate = datetime.datetime.strftime(currentPDate, strDateFormat)

        # logger.info(strCurrentDate)

        outName = f"{varName}_{strCurrentDate}"
        strTempFile = os.path.join(outdir, f"temp_{outName}.tif")
        finalFile = os.path.join(outdir, f"{outName}.tif")

        # First command is like:
        # C:\Continuum\miniconda3_64bit\Library\bin\gdal_translate.exe NETCDF:"D:\temp\n1\PRECIPAH.nc":var -b 2490 -a_srs "+proj=lcc +lat_1=45 +lat_2=45 +lon_0=-120 +lat_0=45.80369 +x_0=0 +y_0=0 +a=6370000 +b=6370000 +units=m" -a_ullr -341997.806, 816645.371, 858002.194, -539354.629 -of GTiff D:\crb_temp\t1.tif
        # TIF output with no compression seems to be fastest on this first step

        strCommand = f'gdal_translate NETCDF:"{infile}":var -b {str(intBand)} {strProjLccSphere} {strNcExtent} -of GTiff {strTempFile}'
        # print(); print(strCommand); print()
        subprocess.check_call(strCommand, shell=True)

        # Clip border 0 cells and create COG
        # 2nd command is like:
        # C:\Continuum\miniconda3_64bit\Library\bin\gdal_translate.exe D:\crb_temp\t1.tif -projwin -337997.806, 812645.371, 854002.194, -535354.629 -of COG -co COMPRESS=LZW -co PREDICTOR=2 D:\crb_temp\PRECIPAH\PRECIPAH_1980_01_12_T17_00.tif

        # Using DEFLATE compression seems to result in smaller file size than LZW but is just a tad slower
        strCommand = f"gdal_translate {strTempFile} {strFinalExtent} -of COG -co COMPRESS=DEFLATE -co PREDICTOR=2 {finalFile}"
        # print(); print(strCommand); print()
        subprocess.check_call(strCommand, shell=True)

        outfile_list.append(
            {
                "filetype": varName,
                "file": finalFile,
                "datetime": currentPDate.replace(
                    tzinfo=datetime.timezone.utc
                ).isoformat(),
                "version": dtVersion.replace(tzinfo=datetime.timezone.utc).isoformat(),
            }
        )

    # fileinfo = info(infile)
    # print(fileinfo)

    strInfo = "All done\n"
    strInfo += "Start time: " + startTime.strftime("%Y-%m-%d %H:%M") + "\n"
    endTime = datetime.datetime.now()
    strInfo += "End time: " + endTime.strftime("%Y-%m-%d %H:%M") + "\n"
    strInfo += "Duration: " + str(endTime - startTime)
    # logger.info(strInfo)

    return outfile_list
    # return []
