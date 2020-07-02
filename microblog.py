import logging

from app import app

app.logger.setLevel(logging.INFO)      #设置等级
app.logger.info('Microblog startup')     #每次启动服务器，往日志中写一句


app.run(debug=True)