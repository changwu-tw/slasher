import time, api, tools, transactions, custom, random

def sign_loop(DB):
    return tools.looper(DB, sign_once, 'sign_loop', 5)
def sign_once(DB):
    acc=tools.db_get(DB['address'], DB)
    for i in range(5):
        sign_on=DB['length']-i-3
        if transactions.signer_p(DB['address'], sign_on, DB):
            secret=str(random.random())+str(random.random())
            DB['secrets'][str(sign_on)]=secret
            secret_hash=tools.det_hash(secret)
            tx={'type':'sign',
                'sign_on':sign_on,
                'rand_nonce':tools.db_get(sign_on, DB)['rand_nonce'],
                'secret_hash':secret_hash}
            api.easy_add_transaction(tx, DB)
def reveal_secrets_loop(DB):
    return tools.looper(DB, reveal_secrets_once, 'reveal_secrets_loop')
def reveal_secrets_once(DB):
    acc=tools.db_get(DB['address'], DB)
    for i in acc['secrets']:
        time.sleep(1)
        start=DB['length']-1000
        if i in range(start, start+800):
            secret=acc['secrets'][i]
            tx={'type':'reveal_secret',
                'sign_on':i,
                'secret':secret,
                'secret_hash':tools.det_hash(secret)}
            api.easy_add_transaction(tx, DB)
            acc['secrets'].pop(i)
def pledge_loop(DB):
    return tools.looper(DB, pledge_loop_once, 'pledge loop once')

def pledge_loop_once(DB):
    acc=tools.db_get(DB['address'], DB)
    if acc['expiration']-DB['length']<800:
        s=DB['length']-99
        tx={'type':'pledge',
            'new':DB['length']+999,
            'old':acc['expiration'],
            'sign_on':s,
            'rand_nonce':tools.db_get(s, DB)['rand_nonce']}
        api.easy_add_transaction(tx, DB)
def buy_blocks(DB):
    pass
    #return tools.looper(DB, api.buy_block, 'buy block loop', 0.1)
