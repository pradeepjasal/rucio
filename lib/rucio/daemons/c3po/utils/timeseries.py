# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Thomas Beermann, <thomas.beermann@cern.ch>, 2015

from redis import StrictRedis
from time import time


class RedisTimeSeries():
    def __init__(self, redis_host, redis_port, window):
        self._r = StrictRedis(host=redis_host, port=redis_port)
        self._prefix = "jobs_"
        self._window = window * 1000000

    def add_point(self, site, jobs):
        name = self._prefix + site
        score = int(time()*1000000)
        self._r.zadd(name, score, "%d:%d" % (jobs, score))

    def get_series(self, site):
        name = self._prefix + site
        r_series = self._r.zrange(name, 0, -1)
        series = []
        for val in r_series:
            jobs, _ = val.split(':')
            series.append(int(jobs))

        return tuple(series)

    def trim(self):
        now = time()
        max_score = int(now*1000000 - self._window)
        for key in self.get_keys():
            self._r.zremrangebyscore(key, 0, max_score)

    def get_keys(self):
        return self._r.keys(pattern="jobs_*")

    def delete_keys(self):
        for key in self.get_keys():
            self._r.zremrangebyrank(key, 0, -1)
