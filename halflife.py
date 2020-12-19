start = 149
add = 70
time=365.0/24.0
hl=28.0
for i in range(1):
    start = add + start * 0.5 ** (time/hl)
    print("lo: %d"   %round(start       * 0.5 ** (time/hl)))
    print("hi: %d\n" %round(add+start   * 0.5 ** (time/hl)))
print(start)
