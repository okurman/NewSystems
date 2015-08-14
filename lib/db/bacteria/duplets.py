__author__ = 'Sanjarbek Hudaiberdiev'

from lib.db import DbClass

def store_kplets_pile(kplets_pile, cdd2id, file2id):

    _sql_kplet = """insert ignore into bacteria_2plets (kplet_1, kplet_2) values \n"""

    _sql_kplet_file = """insert ignore into bacteria_2plets_win10 (kplet_id, file_id) values \n"""

    for (kplets, fname) in kplets_pile:

        for kplet in kplets:
            kplet = list(kplet)
            kplet.sort()
            kplet = tuple([int(cdd2id[k]) for k in kplet])

            _sql_kplet += """(%d, %d),\n""" % kplet

            _sql_kplet_file += ("""((select id from bacteria_2plets where """ +
                                """kplet_1=%d and kplet_2=%d),""" +
                                """%d),\n""") % (kplet + (int(file2id[fname]),))

    _sql_kplet = _sql_kplet[:-2]
    _sql_kplet += ';'

    _sql_kplet_file = _sql_kplet_file[:-2]
    _sql_kplet_file += ';'

    _db = DbClass()

    _db.cmd = _sql_kplet
    _db.execute()
    _db.commit()

    _db.cmd = _sql_kplet_file
    _db.execute()
    _db.commit()


def get_multiple_kplets():

    _db = DbClass()
    _db.cmd = "SET group_concat_max_len = 10000000"
    _db.execute()
    _db.cmd = """ select  ap.id, count(*) cnt, group_concat(convert(apw.file_id, char(15))) as file_ids
                  from bacteria_2plets ap
                  inner join bacteria_2plets_win10 apw on ap.id = apw.kplet_id
                  group by ap.id
                  having count(*)>1
                  order by cnt desc"""

    return _db.retrieve()


def get_code_kplet(kplet_id, id2cdd=None):

    _db = DbClass()

    if not id2cdd:
        _db.cmd = """select cp1.code, cp2.code
                from bacteria_2plets bp
                inner join cdd_profiles cp1 on cp1.id = bp.kplet_1
                inner join cdd_profiles cp2 on cp2.id = bp.kplet_2
                where bp.id = %d""" % kplet_id
        retval = _db.retrieve()[0]

    else:

        _db.cmd = """select kplet_1, kplet_2
                     from bacteria_2plets where id = %d""" % kplet_id

        retval = _db.retrieve()[0]
        retval = set([id2cdd[id] for id in retval])

    return retval


def get_report_kplets(id2cdd, limit_to=500):

    _db = DbClass()
    _db.cmd = """SET group_concat_max_len=1500000"""
    _db.execute()

    _db.cmd = """select ap.* ,count(*) as cnt, sum(w.weight) as wgt, group_concat(awf.name) as an
                 from bacteria_2plets ap
                 inner join bacteria_2plets_win10 apw on ap.id = apw.kplet_id
                 inner join bacteria_win10_files awf on apw.file_id = awf.id
                 inner join sources s on awf.source_id=s.id
                 inner join weights w on w.genome_id=s.genome_id
                 group by ap.id
                 having count(distinct s.genome_id)>1
                 order by wgt desc
                 limit 0, %d""" % limit_to

    out_list = []

    for row in _db.retrieve():
        id = row[0]
        kplet_codes = ([id2cdd[int(id)] for id in row[1:3]])
        count = row[3]
        weight = row[4]
        files = row[5]
        out_list.append([id, kplet_codes, count, weight, files])

    return out_list
