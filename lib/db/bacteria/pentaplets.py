__author__ = 'Sanjarbek Hudaiberdiev'

from lib.db import DbClass


def get_multiple_kplets():

    _cursor = setup_cursor()
    _sql_cmd = """SET group_concat_max_len=15000"""
    _cursor.execute(_sql_cmd)

    _sql_cmd = """select  ap.id, count(*) cnt, group_concat(convert(apw.file_id, char(15))) as file_ids
                  from bacteria_5plets ap
                  inner join bacteria_5plets_win10 apw on ap.id = apw.kplet_id
                  group by ap.id
                  having count(*)>1
                  order by cnt desc"""

    _cursor.execute(_sql_cmd)

    return _cursor.fetchall()


def get_code_kplet(kplet_id):

    _db = DbClass()

    _db.cmd = """select kplet_1, kplet_2, kplet_3, kplet_4, kplet_5 from bacteria_5plets_codes where id = %s""" % kplet_id

    return _db.retrieve()[0]


# def store_kplets(kplets, fname):
#
#     for kplet in kplets:
#         l = list(kplet)
#         l.sort()
#         kplet_id = retrieve_pentaplet_id(l)
#
#         if not kplet_id:
#             insert_pentaplet(l)
#             kplet_id = retrieve_pentaplet_id(l)
#         connection.commit()
#
#         file_id = t.get_file_id(fname)
#         insert_pentaplet_file(kplet_id, file_id)


# def archea_kplet_ids2files(id_list):
#
#     _sql_cmd = """select distinct awf.name
#                   from archea_5plets ap
#                   inner join archea_5plets_win10 apw on ap.id = apw.kplet_id
#                   inner join archea_win10_files awf on apw.file_id = awf.id
#                   where ap.id in (%s)"""
#
#     _cursor = setup_cursor()
#     _cursor.execute(_sql_cmd % " , ".join(id_list))
#     return [l[0] for l in _cursor.fetchall()]
#
#
# def insert_pentaplet_file(kplet_id, file_id):
#     sql_cmd = """insert into archea_5plets_win10 values (%d, %d)"""
#     sql_cmd = sql_cmd%(kplet_id, file_id)
#
#     cursor = setup_cursor()
#     cursor.execute(sql_cmd)
#     connection.commit()
#
#
# def retrieve_pentaplet_id(profiles):
#     profile2id = map_profile2id(profiles)
#
#     sql_cmd = """select id from archea_5plets where kplet_1=%d and kplet_2=%d and kplet_3=%d and kplet_4=%d and kplet_5=%d"""
#     sql_cmd = sql_cmd % (profile2id[profiles[0]], profile2id[profiles[1]], profile2id[profiles[2]], profile2id[profiles[3]], profile2id[profiles[4]])
#
#     cursor = setup_cursor()
#     cursor.execute(sql_cmd)
#     rows = cursor.fetchall()
#
#     if rows:
#         return rows[0][0]
#     return None
#
#
# def insert_pentaplet(profiles):
#     profile2id = map_profile2id(profiles)
#
#     sql_cmd = """insert into archea_5plets (kplet_1, kplet_2, kplet_3, kplet_4, kplet_5) values (%d, %d, %d, %d, %d)"""
#     sql_cmd = sql_cmd%(profile2id[profiles[0]], profile2id[profiles[1]], profile2id[profiles[2]], profile2id[profiles[3]], profile2id[profiles[4]])
#
#     cursor = setup_cursor()
#     cursor.execute(sql_cmd)


def get_report_kplets(id2cdd, limit_to=500):

    _db = DbClass()
    _db.cmd = """SET group_concat_max_len=1500000"""
    _db.execute()

    _db.cmd = """select ap.* ,count(*) as cnt, sum(w.weight) as wgt, group_concat(awf.name) as an
                from bacteria_5plets ap
                inner join bacteria_5plets_win10 apw on ap.id = apw.kplet_id
                inner join bacteria_win10_files awf on apw.file_id = awf.id
                inner join sources s on awf.source_id=s.id
                inner join weights w on w.genome_id=s.genome_id
                group by ap.id
                having count(distinct s.genome_id)>1
                order by wgt desc
                limit 0,%d""" % limit_to

    out_list = []

    for row in _db.retrieve():
        id = row[0]
        kplet_codes = [id2cdd[int(id)] for id in row[1:6]]
        count = row[6]
        weight = row[7]
        files = row[8]
        out_list.append([id, kplet_codes, count, weight, files])

    return out_list
