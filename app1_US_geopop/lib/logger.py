##################################
#encoding=utf8                   #
#version =py27, py33             #
#author  =sanhe                  #
#date    =2014-10-29             #
#                                #
#    (\ (\                       #
#    ( -.-)o    I am a Rabbit!   #
#    o_(")(")                    #
#                                #
##################################

"""一个简单的日志文件夹和日志文件的管理小工具
能很轻易的把捕获到的异常和自定义错误信息写入到日志中
    
Compatible:
    py27, py33

Import:
    from HSH.Misc.logger import Log
"""

from __future__ import print_function
import datetime
import os

class Log(object):
    """
    [CN]usage
        当初始化Log类的时候，会自动在脚本运行所在目录创建一个叫log的目录
        每当try，except时，在人类能预计错误的情况下，可以用
        Log.write(index, message)方法把日志写入名为%Y-%m-%d %H_%M_%S.txt的
        日志文件中。（index和message就可以自己定义了）
        而在无法预知错误的情况下，可以用：
        import sys
        Log.write(index = sys.exc_info()[0], message = sys.exc_info()[1])
        把捕获到的异常写入日志
    """
    
    def __init__(self, directory = "log"):
        """
        [EN]Automatically create a folder named "log" within the same folder with the main script
        [CN]自动在调用此包的主脚本下创建一个"log"的文件夹，可以在初始化时修改
        """
        self.fname = "%s.txt" % datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H_%M_%S")
        self.directory = directory
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

    def clear_all(self):
        """
        [EN]DELETE all log file under #directory
        [CN]删除log目录下所有的日志文件
        """
        cmd = raw_input("Are you sure you want to delete all log file under folder '%s'?\nENTER 'YES' to confirm: " % self.directory)
        if cmd == "YES":
            for fname in os.listdir(self.directory):
                os.remove(os.path.join(self.directory, fname))
            print("All log file under folder '%s' have been deleted." % self.directory)
        else:
            print("DELETE operation canceled.")
            
    def write(self, message, index = "unknown", indent = 1, enable_verbose = True):
        """
        [EN]Write line to local log file. And automatically print log info
        log line format:
            <datetime><index><message>
            
        [Argv]
        ------
        message: log text message
        index: type of this log
        indent: how many indent added to the message head when printing
        enable_verbose: print message while writting to log or not
        
        [CN]把异常信息写入日志，并自动打印出来
        """
        line = "<%s><%s><%s>\n" % (datetime.datetime.now(),
                                   index,
                                   message)
        with open(os.path.join(self.directory, self.fname), "a") as f:
            f.write(line)
        if enable_verbose:
            print("%s%s" % ("\t"*indent, message) ) # print log info