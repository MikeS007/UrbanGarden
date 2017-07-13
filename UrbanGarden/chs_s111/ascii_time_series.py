#******************************************************************************
#
#******************************************************************************
from datetime import datetime
from datetime import timedelta
import pytz

#******************************************************************************
class AsciiTimeSeries:
    

    #******************************************************************************
    def __init__(self, file_name):
        self.file_name = file_name

        self.ascii_file = None
        self.interval = None
        self.start_time = None
        self.end_time = None
        self.number_of_records = 0
        self.current_record = 0
        self.latitude = 0
        self.longitude = 0
        
        #Open the file.
        self.ascii_file = open(self.file_name, 'r')
        
        #Skip the header
        self.read_header()


    #******************************************************************************        
    def read_header(self):
        """Read the header of the time series file."""

        #The header contains 24 rows, so read them all.
        for rowIndex in range(0, 24):

            #Read a line of data
            data = self.ascii_file.readline()

            #If this is the 1st row, then lets decode the start date and time.
            if rowIndex == 0:
                
                #66-66  1 : Units of depth  [m: metres, f: feet]
                self.unit = data[65:66]

                #68-71  4 : Date (Year) of first data record
                year = data[67:71]
                #73-74  2 : Date (Month) of first data record
                month = data[72:74]
                #76-77  2 : Date (Day) of first data record
                day = data[75:77]

            #If this is the 2nd row, then lets decode the x and y positions.
            elif rowIndex == 1:

                #14-15  2 : Latitude (Degrees)
                latDeg = data[13:15]
                #17-23  7 : Latitude (Minutes up to 4 places of decimal)
                latMin = data[16:23]

                self.latitude = float(latDeg) + (float(latMin) / 60.0)

                #24-24  1 : 'N' or 'S'
                if data[23:24] == 'S':
                    self.latitude *= -1.0

                #26-28  3 Longitude (Degrees)
                lonDeg = data[25:28]
                #30-36  7 : Longitude (Minutes up to 4 places of decimal)
                lonMin = data[29:36]

                self.longitude = float(lonDeg) + (float(lonMin) / 60.0)

                #37-37  1 : 'W' or 'E'
                if data[36:37] == 'W':
                    self.longitude *= -1.0


                #62-66  5 : Time Zone [# of hours to add to determine UTC, always include + or - and 
                #           always left justify, (leaves space for Nfld. time). i.e. +03.5]
                utcOffset = data[61:66]

                #68-69  2 : Time (Hour)   of first data record
                hour = data[67:69]
                #70-71  2 : Time (Minute) of first data record
                minute = data[69:71]
                #73-74  2 : Time (Second) of first data record
                seconds = data[72:74]
                
                #We now have enought information to construct our timestamp.
                timeNotInUTC = datetime(year = int(year), month = int(month), day = int(day),
                                                  hour = int(hour), minute = int(minute), second = int(seconds),  tzinfo = pytz.utc)
                                
                self.deltaToUTC = timedelta(hours = float(utcOffset))

                #Store the start time as UTC.
                self.start_time = timeNotInUTC + self.deltaToUTC

            #If this is the 3rd row, then lets decode the number of records in the file.
            elif rowIndex == 2:
                
                #col 01-10 10 : Number of Records to follow header
                self.number_of_records = int(data[0:10])

                #68-69  2 : Sampling interval (Hours)
                sampleHours = data[67:69]
                #70-71  2 : Sampling interval (Minutes)
                sampleMinutes = data[69:71]
                #73-74  2 : Sampling interval (Seconds)
                sampleSeconds = data[72:74]

                self.interval = timedelta(hours = int(sampleHours), minutes = int(sampleMinutes), seconds = int(sampleSeconds))

                #With the start time, number of records, and interval... we can figure out the end time.
                self.end_time = self.start_time + (self.number_of_records - 1) * self.interval


    #******************************************************************************
    def done(self):
        """Determine if we have read all records in the time series file.

        :returns: true if all records have been read, else false.
        """

        if self.current_record < self.number_of_records:
            return False

        return True


    #******************************************************************************
    def read_next_row(self):
        """Read the next row of data from the time series file.

        :returns: A tuple containing the date, direction, and speed (in m/s).
        """

        #If we are done... throw an error.
        if self.done():
            raise Exception('AsciiTimeSeries is done!')

        self.current_record += 1
        asciiData = self.ascii_file.readline()

        dateAndTime = None
        direction = None
        speed = None

        #We expect the following: Date (YYYY/MM/DD), HourMinute (hhmm), Direction (deg T), Speed (m/s) 
        components = asciiData.split()
        if len(components) != 4:
            raise Exception('Record does not have the correct number of values.')

        #decode the date and time, and then covert it to UTC.
        dateAndTime = datetime.strptime(components[0] + components[1], '%Y/%m/%d%H:%M')
        dateAndTime = dateAndTime + self.deltaToUTC
        direction = float(components[2])
        speed = float(components[3])

        #Return a tuple with dateAndTime, direction, and speed
        return (dateAndTime, direction, speed)
