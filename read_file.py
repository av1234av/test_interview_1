import csv
import os
from collections import namedtuple, defaultdict

Trade = namedtuple('Trade',['tradeDate','counterParty','symbol','side','qty','price'])


class AssetRiskReport(object):
    def __init__(self, path):
        self._path = path
        self._position = dict()
        self._tradeVol=defaultdict(int)
        self._prices = defaultdict(float)

    def _calc_position(self, trade):
        pos = self._position.get(trade.symbol, {'Position': 0, 'MktVal':0.0})
        pos['Position'] += trade.qty * (1 if trade.side == 'BUY' else -1)
        self._tradeVol[trade.counterParty] += trade.qty
        # pos['MktVal'] = pos['self._position'] * trade.price
        self._position[trade.symbol] = pos

    def _read_process_marks(self, filename):
        with open(os.path.join(self._path, filename)) as csvfile:

            marksreader = csv.reader(csvfile,  delimiter='\t')
            for row in marksreader:
                self._prices[row[0]]=float(row[1])

    def read_and_process(self):

        for filename in os.listdir(self._path):

            if filename == 'marks.txt':
                self._read_process_marks(filename)
                continue

            with open(os.path.join(self._path, filename)) as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')

                # for trade in map(Trade._make, reader):
                for row in reader:
                    row[4]=int(row[4])          # qty is a numeric integer
                    row[5]=float(row[5])        # price is a float
                    trade=Trade(*row)
                    self._calc_position(trade)

    def generate_report(self):

        for k,v in self._position.iteritems():
            v['MktVal'] = v['Position'] * self._prices[k]

        print '---------- Asset Risk Report ------------'
        for item in sorted(self._position.items(), key=lambda x: x[1]['MktVal'], reverse=True)[:20]:
            print item[0], item[1]['Position'], item[1]['MktVal']

        print '----------- Trade Volume Report ------------'
        for item in sorted(self._tradeVol.items(), key=lambda x: x['TradeVol'], reverse=True)[:20]:
            print item[0], item[1]

if __name__ == '__main__':
    path='C:\\Temp\\test_interview_1\\Data'
    asset_risk_report = AssetRiskReport(path)
    asset_risk_report.read_and_process()
    asset_risk_report.generate_report()