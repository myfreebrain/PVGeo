import numpy as np
import struct
import csv
import os
from vtk.util import numpy_support as nps
import vtk

def readGSLIB(FileName, deli=' ', useTab=False, numIgLns=0):
    """
    Description
    -----------
    Reads a GSLIB file format to a vtkTable. The GSLIB file format has headers lines followed by the data as a space delimited ASCI file (this filter is set up to allow you to choose any single character delimiter). The first header line is the title and will be printed to the console. This line may have the dimensions for a grid to be made of the data. The second line is the number (n) of columns of data. The next n lines are the variable names for the data in each column. You are allowed up to ten characters for the variable name. The data follow with a space between each field (column).

    Parameters
    ----------
    `FileName` : str

    - The absoulte file name with path to read.

    `deli` : str

    - The input files delimeter. To use a tab delimeter please set the `useTab`.

    `useTab` : boolean

    - A boolean that describes whether to use a tab delimeter

    `numIgLns` : int

    - The integer number of lines to ignore

    Returns
    -------
    Retruns a vtkTable of the input data file.

    """

    pdo = vtk.vtkTable() # vtkTable

    if (useTab):
        deli = '\t'

    titles = []
    data = []
    with open(FileName) as f:
        reader = csv.reader(f, delimiter=deli)
        # Skip defined lines
        for i in range(numIgLns):
            next(f)

        # Get file header (part of format)
        header = next(f) # TODO: do something with the header
        #print(os.path.basename(FileName) + ': ' + header)
        # Get titles
        numCols = int(next(f))
        for i in range(numCols):
            titles.append(next(f).rstrip('\r\n'))

        # Read data
        for row in reader:
            data.append(row)

    # Put first column into table
    for i in range(numCols):
        col = []
        for row in data:
            col.append(row[i])
        VTK_data = nps.numpy_to_vtk(num_array=col, deep=True, array_type=vtk.VTK_FLOAT)
        VTK_data.SetName(titles[i])
        pdo.AddColumn(VTK_data)

    return pdo, header




def readPackedBinaries(FileName, dblVals=False, dataNm=''):
    """
    Description
    -----------
    This filter reads in float or double data that is packed into a binary file format. It will treat the data as one long array and make a vtkTable with one column of that data. The reader uses big endian and defaults to import as floats. Use the Table to Uniform Grid or the Reshape Table filters to give more meaning to the data. We chose to use a vtkTable object as the output of this reader because it gives us more flexibility in the filters we can apply to this data down the pipeline and keeps thing simple when using filters in this repository.

    Parameters
    ----------
    `FileName` : str

    - The absoulte file name with path to read.

    `dblVals` : boolean, optional

    - A boolean flag to chose to treat the binary packed data as doubles instead of the default floats.

    `dataNm` : str, optional

    - A string name to use for the construted vtkDataArray

    Returns
    -------
    Retruns a vtkTable of the input data file with a single column being the data read.

    """

    pdo = vtk.vtkTable() # vtkTable

    num_bytes = 4 # FLOAT
    typ = 'f' #FLOAT
    if dblVals:
        num_bytes = 8 # DOUBLE
        typ = 'd' # DOUBLE

    tn = os.stat(FileName).st_size / num_bytes
    tn_string = str(tn)
    raw = []
    with open(FileName, 'rb') as file:
        # Unpack by num_bytes
        raw = struct.unpack('>'+tn_string+typ, file.read(num_bytes*tn))

    # Put raw data into vtk array
    data = nps.numpy_to_vtk(num_array=raw, deep=True, array_type=vtk.VTK_FLOAT)

    # If no name given for data by user, use the basename of the file
    if dataNm == '':
        dataNm = os.path.basename(FileName)
    data.SetName(dataNm)

    # Table with single column of data only
    pdo.AddColumn(data)

    return pdo


def readDelimetedFile(FileName, deli=' ', useTab=False, hasTits=True, numIgLns=0):
    """
    Description
    -----------
    This reader will take in any delimited text file and make a vtkTable from it. This is not much different than the default .txt or .csv reader in Paraview, however it gives us room to use our own extensions and a little more flexibility in the structure of the files we import.


    Parameters
    ----------
    `FileName` : str

    - The absoulte file name with path to read.

    `deli` : str

    - The input files delimeter. To use a tab delimeter please set the `useTab`.

    `useTab` : boolean

    - A boolean that describes whether to use a tab delimeter

    `numIgLns` : int

    - The integer number of lines to ignore

    Returns
    -------
    Retruns a vtkTable of the input data file.

    """
    pdo = vtk.vtkTable() # vtkTable

    if (useTab):
        deli = '\t'

    titles = []
    data = []
    with open(FileName) as f:
        reader = csv.reader(f, delimiter=deli)
        # Skip header lines
        for i in range(numIgLns):
            reader.next()
        # Get titles
        if (hasTits):
            titles = reader.next()
        else:
            # Bulild arbitrary titles for length of first row
            row = reader.next()
            data.append(row)
            for i in range(len(row)):
                titles.append('Field' + str(i))
        # Read data
        for row in reader:
            data.append(row)

    # Put columns into table
    for i in range(len(titles)):
        col = []
        for row in data:
            col.append(row[i])
        VTK_data = nps.numpy_to_vtk(num_array=col, deep=True, array_type=vtk.VTK_FLOAT)
        VTK_data.SetName(titles[i])
        pdo.AddColumn(VTK_data)

    return pdo