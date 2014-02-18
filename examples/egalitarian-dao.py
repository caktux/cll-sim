from sim import Block, Contract, Tx, Simulation, log, mktx, stop

class EgalitarianDao(Contract):
    """Egalitarian DAO contract example"""

    def run(self, tx, contract, block):
        k = 1000

        if tx.value < block.basefee * 200:
            stop("Insufficient fee")
        if contract.storage[k] == 0:
            if tx.value < 1000 * 10 ** 18:
                stop("Insufficient value")
        if contract.storage[k] == 0:
            if contract.storage[k + 1] == 0:
                contract.storage[k] = 1
                contract.storage[k + 3] += tx.value - block.basefee * 200
                stop(tx.sender + " is in.")
        elif contract.storage[k] == 1 and contract.storage[k + 1] == 0:
            if tx.value < 1000 * 10 ** 18:
                stop("Insufficient fee for storage")
            if contract.storage[k + 2] == 0:
                contract.storage[k + 1] = 1
                contract.storage[k + 3] += tx.value - block.basefee * 200
                stop(tx.sender + " is in.")
        elif contract.storage[k + 1] == 1 and contract.storage[k + 2] == 0:
            if tx.value < 1000 * 10 ** 18:
                stop("Insufficient fee for storage")
            contract.storage[k + 2] = 1
            contract.storage[k + 3] += tx.value - block.basefee * 200
            stop(tx.sender + " is in.")
        elif contract.storage[k + 3] > 0 and tx.value <= 1000 * 10 ** 18:
            if contract.storage[k + 3] < tx.value * 3:
                stop("Insufficient funds for withdrawal")
            if tx.value <= block.basefee * 200:
                stop("Insufficient fee for withdrawal")

            mktx(A, contract.storage[k + 3] / 30, 0, 0)
            mktx(B, contract.storage[k + 3] / 30, 0, 0)
            mktx(C, contract.storage[k + 3] / 30, 0, 0)

            contract.storage[k + 3] -= contract.storage[k + 3] / 3


class EgalitarianDaoRun(Simulation):

    contract = EgalitarianDao(A="alice", B="bob", C="charles", D="dao")
    ts_zero = 1392632520
    deposit = 2000 * 10 ** 18

    def test_insufficient_fee(self):
        tx = Tx(sender='alice', value=10)
        self.run(tx, self.contract)
        assert self.stopped == 'Insufficient fee'

    def test_insufficient_value(self):
        tx = Tx(sender='alice', value=1000)
        self.run(tx, self.contract)
        assert self.stopped == 'Insufficient value'
        assert self.contract.storage[1000] == 0

    def test_creation(self):
        block = Block(timestamp=self.ts_zero)
        tx = Tx(sender='alice', value=self.deposit)
        self.run(tx, self.contract, block)
        tx = Tx(sender='bob', value=self.deposit)
        self.run(tx, self.contract, block)
        tx = Tx(sender='charles', value=self.deposit)
        self.run(tx, self.contract, block)
        assert self.contract.storage[1000] == 1
        assert self.contract.storage[1001] == 1
        assert self.contract.storage[1002] == 1
        assert self.contract.storage[1003] == (self.deposit * 3) - ((block.basefee * 200) * 3)
        assert len(self.contract.txs) == 0

    def test_one_withdraws(self):
        block = Block(timestamp=self.ts_zero + 15 * 86400 + 1)
        block.contract_storage(self.contract.D)[self.contract.D] = 100000 * 10 ** 18
        tx = Tx(sender='alice', value=1000)
        self.run(tx, self.contract, block)
        assert len(self.contract.txs) == 3
        assert self.contract.txs == [('alice', 199999999999999999980, 0, 0), ('bob', 199999999999999999980, 0, 0), ('charles', 199999999999999999980, 0, 0)]

    def test_two_withdraws(self):
        block = Block(timestamp=self.ts_zero + 30 * 86400 + 1)
        block.contract_storage(self.contract.D)[self.contract.D] = 100000 * 10 ** 18
        tx = Tx(sender='alice', value=1000)
        self.run(tx, self.contract, block)
        tx = Tx(sender='bob', value=1000)
        self.run(tx, self.contract, block)
        assert len(self.contract.txs) == 3
        assert self.contract.txs == [('alice', 88888888888888888880, 0, 0), ('bob', 88888888888888888880, 0, 0), ('charles', 88888888888888888880, 0, 0)]
