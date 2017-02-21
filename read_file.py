import csv
import os
from collections import namedtuple, defaultdict

Trade = namedtuple('Trade',['tradeDate','counterParty','symbol','side','qty','price'])


class AssetRiskReport(object):
    TOP_N = 20

    def __init__(self, path):
        self._path = path
        self._position = dict()
        self._tradeVol=defaultdict(int)
        self._prices = defaultdict(float)

    def _calc_position(self, trade):
        pos = self._position.get(trade.symbol, {'Position': 0, 'MktVal':0.0, 'OrderPrice':0.0})
        pos['Position'] += trade.qty * (1 if trade.side == 'BUY' else -1)
        pos['OrderPrice'] = trade.price
        self._tradeVol[trade.counterParty] += trade.qty
        self._position[trade.symbol] = pos

    def _read_process_marks(self, filename):
        with open(os.path.join(self._path, filename)) as csvfile:

            marksreader = csv.reader(csvfile,  delimiter='\t')
            for row in marksreader:
                self._prices[row[0]]=float(row[1])

    def read_and_process(self):

        # walk the current directory and process files
        for dirpath, dir, filenames in os.walk(self._path):

            for filename in filenames:
                if filename == 'marks.txt':
                    self._read_process_marks(filename)
                    continue

                with open(os.path.join(dirpath, filename)) as csvfile:
                    reader = csv.reader(csvfile, delimiter='\t')

                    # for trade in map(Trade._make, reader):
                    for row in reader:
                        row[4]=int(row[4])          # qty is a numeric integer
                        row[5]=float(row[5])        # price is a float
                        trade=Trade(*row)
                        self._calc_position(trade)

    def generate_report(self):

        for k,v in self._position.iteritems():
            # if missing marks then use the last order price as the current price.
            v['MktVal'] = v['Position'] * (self._prices[k] if self._prices[k] else v['OrderPrice'])

        print '---------- Asset Risk Report ------------'
        # sort the positions based on mktval
        # filter out the long positions
        # return the top 20

        for item in filter(lambda x: x[1]['MktVal'] > 0, \
                           sorted(self._position.items(), key=lambda x: x[1]['MktVal'], reverse=True))[:self.TOP_N]:
            print item[0], item[1]['Position'], item[1]['MktVal']

        print '----------- Trade Volume Report ------------'
        for item in sorted(self._tradeVol.items(), key=lambda x: x[1], reverse=True)[:self.TOP_N]:
            print item[0], item[1]

if __name__ == '__main__':
    path=os.path.join(os.getcwd(), 'Data')
    asset_risk_report = AssetRiskReport(path)
    asset_risk_report.read_and_process()
    asset_risk_report.generate_report()
