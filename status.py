#!/usr/bin/python

# $Id:$ 

class Status:
    pass

status = Status()

status.active_downloads = 0


status.download_successes = 0
status.download_failures = 0
status.curl_total_time = []
status.curl_namelookup_time = []
status.curl_connect_time = []
status.curl_speed_download = []
                                  
