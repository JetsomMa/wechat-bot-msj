import pymysql

def getConnection():
    # 创建数据库连接
    connection = pymysql.connect( host='118.195.236.91', user='dataset', password='dataset2023', db='dataset' )

    # 创建一个游标对象
    cursor = connection.cursor()
    print("数据库连接成功！")
    return connection, cursor

def closeConnection(connection, cursor):
    # 关闭游标和连接对象
    cursor.close()
    connection.close()
    print("数据库连接关闭成功！")

def getJiancaiConfig():
    connection, cursor = getConnection()
    cursor.execute("SELECT keywords, keywordsnotneed, targetcontact, blacklist FROM jiancai_config")
    result = cursor.fetchall()
    print("数据查询成功：" + str(len(result)) + "条数据！")
    closeConnection(connection, cursor)
    return result
