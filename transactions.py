"""This file explains how we tell if a transaction is valid or not, it explains
how we update the database when new transactions are added to the blockchain."""
import blockchain, custom, copy, tools, txs_tools
E_check=tools.E_check
def sigs_match(Sigs, Pubs, msg):
    pubs=copy.deepcopy(Pubs)
    sigs=copy.deepcopy(Sigs)
    def match(sig, pubs, msg):
        for p in pubs:
            if tools.verify(msg, sig, p):
                return {'bool':True, 'pub':p}
        return {'bool':False}
    for sig in sigs:
        a=match(sig, pubs, msg)
        if not a['bool']:
            return False
        sigs.remove(sig)
        pubs.remove(a['pub'])
    return True
def signature_check(tx):
    tx_copy = copy.deepcopy(tx)
    if not E_check(tx, 'signatures', list):
        tools.log('no signautres')
        return False
    if not E_check(tx, 'pubkeys', list):
        tools.log('no pubkeys')
        return False
    tx_copy.pop('signatures')
    if len(tx['pubkeys']) == 0:
        tools.log('pubkey error')
        return False
    if len(tx['signatures']) > len(tx['pubkeys']):
        tools.log('sigs too long')
        return False
    msg = tools.det_hash(tx_copy)
    if not sigs_match(copy.deepcopy(tx['signatures']),
                      copy.deepcopy(tx['pubkeys']), msg):
        tools.log('sigs do not match')
        return False
    return True
def spend_verify(tx, txs, DB):
    #do we need to pledge to a blockchain?
    address=tools.addr(tx)
    acc=tools.db_get(address, DB)
    if acc['blacklist']=='true': return False
    if not E_check(tx, 'to', [str, unicode]):
        tools.log('no to')
        return False
    if not signature_check(tx):
        tools.log('signature check')
        return False
    if len(tx['to'])<=30:
        tools.log('that address is too short')
        tools.log('tx: ' +str(tx))
        return False
        return False
    if not E_check(tx, 'amount', int):
        tools.log('no amount')
        return False
    if not txs_tools.fee_check(tx, txs, DB):
        tools.log('fee check error')
        return False
    return True
def seed_range(start, end, DB):
    seeds=[]
    for i in range(start, end):
        if i<0: 
            seeds.append(i)
        else:
            block=tools.db_get(str(i), DB)
            for tx in block['txs']:
                if tx['type']=='reveal_secret':
                    seeds.append(tx['secret'])
    return tools.det_hash(seeds)
def sign_verify(tx, txs, DB):
    #were we elected 3000 blocks ago?
    #SHA256(all the seeds in the last 100 blocks on the old chain, addr(tx))<2^256 *64*balance/(total money supply)
    address=tools.addr(tx)
    acc=tools.db_get(address, DB)
    if acc['blacklist']=='true': 
        tools.log('blocklisted address: ' +str(address))
        return False
    if not E_check(tx, 'sign_on', int):
        tools.log('no secret_hash')
        return False
    if tx['sign_on']<DB['length']-10:
        return False
    for sh in acc['secret_hashes']:
        if sh[1]==tx['sign_on']:
            #tools.log('already signed on that block')
            return False
    for t in txs:
        if t['type']==tx['type']:
            if t['sign_on']==tx['sign_on']:
                if tools.addr(t)==address:
                    #tools.log('already signed on that block, in a different zero confirmation transaction')
                    return False
    if not signature_check(tx):
        tools.log('signature check')
        return False
    if not E_check(tx, 'secret_hash', [str, unicode]):
        tools.log('no secret_hash')
        return False
    if not E_check(tx, 'rand_nonce', [str, unicode]):
        tools.log('no rand_nonce')
        return False
    block=tools.db_get(tx['sign_on'], DB)
    if tx['rand_nonce']!=block['rand_nonce']:
        '''
        bad block-tx error: {u'count': 121, u'signatures': [u'G8B2MY84ycJRtxl9TmkkGewmfIx4kAINBvlzXzgvBSd05FL+KXDqOla6hRkFlnR25sLvlvUFb7dI7zwz+G8CMqk='], u'type': u'sign', u'block_hash': u'dd63f36259796629031b8e096666fb97531bbbf750a6b90c9ea9ee931a07a345', u'sign_on': 115, u'pubkeys': [u'0444b7b6190c2b23e5580bbe35db85ffac275e2562d007f950e240d5f01ba24ed5c8f1d5cba845f7c27a1546ff67af866683eef2ba3088c7bc0e4e4f4769bd31a0'], u'secret_hash': u'b9221333e62943024f0b87ccd5881a0aa0d7ac9d6c0a4e1fafe693c05d420389'}
        in block: {u'count': 97, u'signatures': [u'G5m+gUXDlK+2Kop3ob2uRBvso8I2BVekf6eth/gtrcEBnk8PVmC6v8nMtMimrSe9c/p0Q5cq4/lx2JdT195mXls='], u'sig_length': 1, u'length': 123, u'version': u'VERSION', u'pubkeys': [u'0444b7b6190c2b23e5580bbe35db85ffac275e2562d007f950e240d5f01ba24ed5c8f1d5cba845f7c27a1546ff67af866683eef2ba3088c7bc0e4e4f4769bd31a0'], u'prevHash': u'6b6886752ca24402bd27527798395b356b1ac20cb094a013ac99c8aac2541994', u'txs': [{u'count': 121, u'signatures': [u'G8B2MY84ycJRtxl9TmkkGewmfIx4kAINBvlzXzgvBSd05FL+KXDqOla6hRkFlnR25sLvlvUFb7dI7zwz+G8CMqk='], u'secret_hash': u'b9221333e62943024f0b87ccd5881a0aa0d7ac9d6c0a4e1fafe693c05d420389', u'block_hash': u'dd63f36259796629031b8e096666fb97531bbbf750a6b90c9ea9ee931a07a345', u'sign_on': 115, u'pubkeys': [u'0444b7b6190c2b23e5580bbe35db85ffac275e2562d007f950e240d5f01ba24ed5c8f1d5cba845f7c27a1546ff67af866683eef2ba3088c7bc0e4e4f4769bd31a0'], u'type': u'sign'}]}
        sign block_hash does not match
        '''
        tools.log('sign block_hash does not match')
        return False
    if not signer_p(address, tx['sign_on'], DB):
        tools.log('you were not elected as a signer error')
        return False
    return True
def signer_p(address, sign_on, DB):
    seeds=seed_range(sign_on-2000, sign_on-1900, DB)
    my_size=tools.det_hash(seeds+address)
    balance=blockchain.old_chain(lambda DB: tools.db_get(address, DB)['amount'], DB)
    if type(balance)!=type(1):
        return False
    target=tools.target_times_float('f'*64, 64*balance/custom.total_money)
    size=max(len(my_size), len(target))
    return tools.buffer_(my_size, size)<=tools.buffer_(target, size)
def reveal_secret_verify(tx, txs, DB):
    address=tools.addr(tx)
    acc=tools.db_get(address, DB)
    if not E_check(tx, 'sign_on', int):
        tools.log('what length did you sign')
        return False
    if tx['sign_on']>=DB['length']-100:
        tools.log('too soon')
        return False
    if tx['sign_on']<=DB['length']-1000:
        tools.log('too late')
        return False
    if not signature_check(tx):#otherwise miners will censor his reveal.
        tools.log('signature check')
        return False
    for s in acc['secrets']:
        if s[1]==tx['sign_on']:
            tools.log('already revealed the secret stored at that length')
        if s[0]==tx['secret']:
            tools.log('already revealed that secret')
            return False
    for t in txs:
        if t['type']==tx['type']:
            if tools.addr(t)==address:
                if t['sign_on']==tx['sign_on']:
                    tools.log('already revealed that length in a different zeroth confirmation tx')
                    return False
    if not E_check(tx, 'secret_hash', [str, unicode]):
        tools.log('no secret_hash')
        return False
    if not E_check(tx, 'secret', [str, unicode]):
        tools.log('no secret')
        return False
    for sh in acc['secret_hashes']:
        if sh[1]==tx['sign_on']:
            hash_=sh[0]
    if not det_hash(tx['secret'])==hash_:
        tools.log('secret does not match secret_hash')
        return False
    return True
def sign_slasher_verify(tx, txs, DB):
    if not signatures_check(tx['tx1']): return False
    if not signatures_check(tx['tx2']): return False
    if tools.addr(tx['tx1'])!=tools.addr(tx['tx2']): return False
    address=tools.addr(tx['tx1'])
    acc=tools.db_get(address, DB)
    if acc['expiration']<DB['length']: return False
    for sh in acc['secret_hashes']:
        flag=True
        if sh[1]==tx['tx1']['sign_on']:
            flag=False
        if flag:
            return False
    if tx['tx1']['sign_on'] != tx['tx2']['sign_on']: return False
    if tx['tx1']['type'] != tx['tx2']['type']: return False
    if tx['tx1']['type'] != 'sign': return False
    if tx['tx1']['block_hash'] == tx['tx2']['block_hash']: return False
    return True
def pledge_verify(tx, txs, DB):
    address=tools.addr(tx)
    acc=tools.db_get(address, DB)
    if not E_check(tx, 'old', int):
        tools.log('no old_expiration')
        return False
    if acc['expiration']!=tx['old']:
        tools.log('wrong old')
        return False
    if not E_check(tx, 'new', int):
        tools.log('no new_expiration')
        return False
    if not E_check(tx, 'rand_nonce', [str, unicode]):
        tools.log('no rand_nonce')
        return False
    block=tools.db_get(tx['sign_on'], DB)
    if tx['rand_nonce']!=block['rand_nonce']:
        print('tx: ' +str(tx))
        print('block: ' +str(block))
        tools.log('pledge rand_nonce does not match')
        return False
    if tx['sign_on']>DB['length']-50: return False
    if tx['sign_on']<DB['length']-100: return False
    if not signature_check(tx):
        tools.log('signature check')
        return False
    if not txs_tools.fee_check(tx, txs, DB):
        tools.log('not enough funds tx error')
    if tx['old']-DB['length']>800:
        tools.log('you pledged too recently')
        return False
    if tx['new']-DB['length']>1000:
        tools.log('that is too far into the future')
        return False
    if tx['new']-DB['length']<900:
        tools.log('that is not far enough into the future')
        return False
    return True
def pledge_slasher_verify(tx, txs, DB):
    #do NOT check for a signature, anyone can spend this.
    #make it impossible to slash the same thing twice
    address=tools.addr(tx['tx1'])
    if not E_check(tx, 'old', int):
        tools.log('no old_expiration')
        return False
    if not E_check(tx, 'rand_nonce', [str, unicode]):
        tools.log('no rand_nonce')
        return False
    if not signatures_check(tx['tx1']): return False
    if not tx['tx1']['type']=='pledge': return False
    if tx['tx1']['rand_nonce']==tx['txs2']['rand_nonce']: return False
    acc=tools.db_get(address, DB)
    block=tools.db_get(tx['tx1']['old'], DB)
    if tx['tx1']['rand_nonce']==block['rand_nonce']:
        tools.log('rand_nonce does match')
        return False
    if acc['blacklist']=='true': return False
    return True
tx_check = {'spend':spend_verify,
            'sign':sign_verify,
            'reveal_secret':reveal_secret_verify,
            'sign_slasher':sign_slasher_verify,
            'pledge':pledge_verify,
            'pledge_slasher':pledge_slasher_verify}
#------------------------------------------------------
adjust_int=txs_tools.adjust_int
adjust_dict=txs_tools.adjust_dict
adjust_list=txs_tools.adjust_list
symmetric_put=txs_tools.symmetric_put
def spend(tx, DB):
    address = tools.addr(tx)
    adjust_int(['amount'], address, -tx['amount'], DB)
    adjust_int(['amount'], tx['to'], tx['amount'], DB)
    adjust_int(['amount'], address, -custom.fee, DB)
    adjust_int(['count'], address, 1, DB)
def sign(tx, DB):
    address = tools.addr(tx)
    adjust_int(['count'], address, 1, DB)
    adjust_list(['secret_hashes'], address, False, [tx['secret_hash'], tx['sign_on']], DB)#list to dict
    #DB['sig_length'] should get longer.
def reveal_secret(tx, DB):
    #reveals secret, pays reward
    address=tools.addr(tx)
    adjust_int('count', address, 1, DB)
    adjust_int('amount', address, custom.pos_reward, DB)
    adjust_list(['secrets'], address, False, [tx['secret'], tx['sign_on']], DB)#list to dict
    #adjust_list('secret_hashes', tx['sign_on'], True, secret(tx), DB)
    #adjust_list('secrets', tx['sign_on'], False, tx['secret'], DB)
def sign_slasher(tx, DB):
    t=tx['tx1']#<--this tx is on our chain
    address=tools.addr(t)
    adjust_list(['secret_hashes'], address, True, [t['secret_hash'], t['sign_on']])
def pledge(tx, DB):
    address=tools.addr(tx)
    acc=tools.db_get(address, DB)
    adjust_int(['expiration'], address, tx['new']-tx['old'], DB)
    adjust_int(['amount'], address, custom.pledge_fee, DB)
    pass
def pledge_slasher(tx, DB):
    address=tools.addr(tx['tx1'])
    acc=tools.db_get(address, DB)
    adjust_string(['blacklist'], address, 'false', 'true', DB)
    #destroys someone's monoey, and gives 4/5ths to someone else
    '''
    address=tools.addr(tx)
    criminal=tools.addr(tx['tx1'])
    adjust_int('count', address, 1, DB)
    adjust_int('amount', criminal, custom.pos_reward/3, DB)
    adjust_list('secret_hashes', tx['tx1']['sign_on'], False, tx['secret_hash'], DB)
    '''

update = {'spend':spend,
          'sign':sign,
          'reveal_secret':reveal_secret,
          'sign_slasher':sign_slasher,
          'pledge':pledge,
          'pledge_slasher':pledge_slasher}
