import macDb

macDb.store('aa:bb:cc', 'Comp A')
macDb.store('bb:bb:cc', 'Comp B')
macDb.store('cc:bb:cc', 'Comp C')

res = macDb.get('aa:bb:cc')
if (1 == 2):
    print("juhu")
else:
    print(res)

macDb.close()
