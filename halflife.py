start = 0
add = 70
time=365.0/24.0
hl=28.0
for i in range(45):
    start = add + start * 0.5 ** (time/hl)
    print("lo: %d"   % round(start       * 0.5 ** (time/hl)))
    print("hi: %d\n" % round(add + start * 0.5 ** (time/hl)))
# print(start)

print(265 * 0.5 ** (21.0/28.0))
