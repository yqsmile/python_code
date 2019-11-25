#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: yczhang
# @Date  : 2019/11/25
# @Description  :

from netCDF4 import Dataset, num2date, date2num
import numpy as np
import os


def conv_nc2txt():
    filename = "./data/2018.nc"
    output = "./output/2018.txt"
    ncObj = Dataset(filename)
    vars = ncObj.variables.keys()
    dims = ncObj.dimensions.keys()
    y = list(set(vars).difference(set(dims)))
    assert len(y) != 0

    Y0 = ncObj.variables[y[0]]
    keys = [key.name for key in Y0.get_dims()]

    headers = keys + y
    str_headers = ''
    for i in headers:
        str_headers += i + '\t'
    str_headers = str_headers + '\n'
    if not os.path.exists(output):
        with open(output, "w") as f:
            f.write(str_headers)

    dims_val = {}
    var_val = {}
    for key in keys:
        if key == 'time':
            times = ncObj.variables[key]
            dims_val[key] = num2date(times[:], units=times.units, calendar=times.calendar)
            continue
        dims_val[key] = ncObj.variables[key][:]

    assert len(keys) >= 2
    if len(keys) >= 2:
        X = dims_val[keys[0]]
        for i in range(1, len(keys)):
            X = cartesian(X, dims_val[keys[i]])
    cartesian_val = X
    Y0 = np.array(Y0[:]).flatten()
    assert len(Y0) == len(cartesian_val)

    for item in y:
        var_val[item] = np.array(ncObj.variables[item][:]).flatten()
        assert len(var_val[item]) == len(cartesian_val)

    with open(output, "a") as f:
        for i in range(len(cartesian_val)):
            line = cartesian_val[i] + '\t'
            for item in y:
                line += str(var_val[item][i]) + '\t'
            line += '\n'
            f.write(line)


def cartesian(lst_x: list, lst_y: list):
    return [str(str(x) + '\t' + str(y) + '\t') for x in lst_x for y in lst_y]


if __name__ == '__main__':
    conv_nc2txt()
