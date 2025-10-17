# 调用函数求解
import z3
import re

def add_conditions_to_solver(conds, solver, filesize_value, uint_array, uint32_array):
    """
    将用户提供的条件字符串（conds）转化为Z3表达式并添加到求解器中。
    
    Args:
    conds (str): 包含多个条件的字符串，每个条件之间换行。
    solver (z3.Solver): Z3求解器实例。
    filesize (int): 文件大小，用于条件中涉及的 "filesize" 变量。
    uint_array (z3.Array): 用于存放需要求解的 uint 数组。
    """
    # 解析用户输入的条件
    for cond in conds.split("\n"):
        if cond.strip() == "":  # 跳过空行
            continue
        
        # 根据条件内容动态构建Z3表达式并添加到求解器
        if "hash.md5" in cond:
            # 解析 hash.md5 条件，例如: hash.md5(0, 2) == "89484b14b36a8d5329426a3d944d2983"
            match = re.match(r'hash\.md5\((\d+),\s*(\d+)\)\s*==\s*"([0-9a-fA-F]+)"', cond)
            if match:
                start = int(match.group(1))
                length = int(match.group(2))
                hash_value = match.group(3)
                # 由于z3无法直接处理MD5，记录约束信息以便后续处理
                solver.add(z3.Bool(f"md5_constraint_{start}_{length}_{hash_value}"))
            else:
                raise ValueError(f"无法解析条件: {cond}")

        elif "filesize" in cond:
            if "^" in cond:
                idx = int(cond.split("uint8(")[1].split(")")[0].strip())
                if "!=" in cond:
                    value = int(cond.split("!=")[1].strip())

                    solver.add(filesize_value ^ uint_array[idx] != value)
                else:
                    value = int(cond.split("==")[1].strip())

                    solver.add(filesize_value ^ uint_array[idx] == value)
            else:
                value = int(cond.split("==")[1].strip())
                solver.add(filesize_value == value)

        elif "uint8" in cond:
            # 处理 uint8 类型的条件
            idx = int(cond.split("(")[1].split(")")[0].strip())
            if ">" in cond:
                value = int(cond.split(">")[1].strip())
                solver.add(uint_array[idx] > value)
            elif "<" in cond:
                value = int(cond.split("<")[1].strip())
                solver.add(uint_array[idx] < value)
            elif "==" in cond:
                value = int(cond.split("==")[1].strip())
                solver.add(uint_array[idx] == value)
            elif "&" in cond:
                value = int(cond.split("&")[1].strip())
                solver.add(uint_array[idx] & value == 0)
            elif "%" in cond:
                value = int(cond.split("%")[1].strip())
                solver.add(uint_array[idx] % value < value)

        elif "uint32" in cond:
            # 处理 uint32 类型的条件
            idx = int(cond.split("(")[1].split(")")[0].strip())
            if "^" in cond: 
                value = int(cond.split("^")[1].split("==")[0].strip())
                solver.add(uint32_array[idx] ^ value == int(cond.split("==")[1].strip()))
            elif "-" in cond:
                value = int(cond.split("-")[1].strip().split("==")[0].strip())
                solver.add(uint32_array[idx] - value == int(cond.split("==")[1].strip()))
            elif "+" in cond:
                value = int(cond.split("+")[1].strip().split("==")[0].strip())
                solver.add(uint32_array[idx] + value == int(cond.split("==")[1].strip()))

def solve_yara_conditions(conds):
    solver = z3.Solver()

    filesize_value = z3.BitVec('filesize_value', z3.BitVecSort(32))
    solver.add(filesize_value == 88)

    # 定义 uint 数组，求解 filesize 个数组元素
    uint_array = z3.Array('uint_array', z3.IntSort(), z3.BitVecSort(32))
    for i in range(88):
        solver.add(uint_array[i] >= 0, uint_array[i] < 256)

    uint32_array = z3.Array('uint32_array', z3.IntSort(), z3.BitVecSort(32))
    
    # 将用户提供的条件转化为Z3表达式并添加到求解器中
    add_conditions_to_solver(conds, solver, filesize_value, uint_array, uint32_array)

    # 解决器检查并返回是否满足所有约束
    if solver.check() == z3.sat:
        model = solver.model()
        return model
    else:
        return "Unsatisfiable"

# 示例条件
conds = """
filesize == 85
filesize ^ uint8(11) != 107
uint8(55) & 128 == 0
uint8(58) + 25 == 122
uint8(7) & 128 == 0
uint8(48) % 12 < 12
uint8(17) > 31
uint8(68) > 10
uint8(56) < 155
uint32(52) ^ 425706662 == 1495724241
uint8(0) % 25 < 25
filesize ^ uint8(75) != 25
filesize ^ uint8(28) != 12
uint8(35) < 160
uint8(3) & 128 == 0
uint8(56) & 128 == 0
uint8(28) % 27 < 27
uint8(4) > 30
uint8(15) & 128 == 0
uint8(68) % 19 < 19
uint8(19) < 151
filesize ^ uint8(73) != 17
filesize ^ uint8(31) != 5
uint8(38) % 24 < 24
uint8(3) > 21
uint8(54) & 128 == 0
filesize ^ uint8(66) != 146
uint32(17) - 323157430 == 1412131772
hash.crc32(8, 2) == 0x61089c5c
filesize ^ uint8(77) != 22
uint8(75) % 24 < 24
uint8(66) < 133
uint8(21) % 11 < 11
uint8(46) < 154
hash.crc32(34, 2) == 0x5888fc1b
uint8(55) > 5
uint8(36) + 4 == 72
filesize ^ uint8(82) != 228
filesize ^ uint8(13) != 42
filesize ^ uint8(6) != 39
uint8(33) < 160
filesize ^ uint8(55) != 244
filesize ^ uint8(15) != 205
filesize ^ uint8(3) != 43
filesize ^ uint8(54) != 39
uint8(28) & 128 == 0
uint8(10) < 146
filesize ^ uint8(56) != 246
filesize ^ uint8(32) != 77
uint8(73) > 26
uint8(36) > 11
uint8(70) > 6
filesize ^ uint8(33) != 27
uint8(48) & 128 == 0
filesize ^ uint8(74) != 45
uint8(27) ^ 21 == 40
uint8(60) % 23 < 23
filesize ^ uint8(67) != 63
filesize ^ uint8(0) != 16
uint8(51) % 15 < 15
uint8(50) > 19
uint8(27) < 147
filesize ^ uint8(40) != 230
filesize ^ uint8(2) != 205
uint8(79) % 24 < 24
uint8(69) < 148
uint8(16) & 128 == 0
uint8(61) % 26 < 26
uint8(63) > 31
uint8(14) & 128 == 0
uint8(35) > 1
filesize ^ uint8(11) != 33
uint8(52) < 136
uint8(54) > 15
filesize ^ uint8(20) != 83
uint8(43) > 24
uint8(82) < 152
uint32(59) ^ 512952669 == 1908304943
filesize ^ uint8(79) != 186
filesize ^ uint8(83) != 197
uint8(39) < 134
filesize ^ uint8(43) != 33
uint8(72) > 10
uint8(83) < 134
uint8(44) % 27 < 27
uint8(40) < 131
uint8(80) % 31 < 31
filesize ^ uint8(47) != 11
uint8(55) % 11 < 11
filesize ^ uint8(71) != 3
uint8(65) - 29 == 70
uint8(58) > 30
filesize ^ uint8(37) != 37
uint8(60) < 130
uint8(27) & 128 == 0
uint8(3) < 141
uint8(73) & 128 == 0
filesize ^ uint8(70) != 209
filesize ^ uint8(2) != 54
filesize ^ uint8(20) != 17
uint8(33) > 18
uint8(37) % 19 < 19
filesize ^ uint8(62) != 15
filesize ^ uint8(10) != 44
uint8(7) % 12 < 12
uint8(71) > 19
filesize ^ uint8(50) != 86
uint8(45) ^ 9 == 104
uint8(8) < 133
uint8(31) < 145
uint8(14) > 20
uint8(54) % 25 < 25
filesize ^ uint8(49) != 156
uint8(47) > 13
uint8(29) > 22
uint8(14) % 19 < 19
filesize ^ uint8(17) != 16
filesize ^ uint8(12) != 226
filesize ^ uint8(65) != 28
uint8(45) & 128 == 0
filesize ^ uint8(6) != 129
uint8(18) % 30 < 30
filesize ^ uint8(62) != 246
uint8(78) % 13 < 13
uint8(36) & 128 == 0
uint8(10) & 128 == 0
uint8(62) > 1
uint8(33) & 128 == 0
filesize ^ uint8(83) != 31
uint8(83) % 21 < 21
uint8(11) > 18
uint8(80) < 143
uint8(81) % 14 < 14
uint8(43) < 160
uint8(1) > 19
uint8(42) % 17 < 17
uint8(44) < 147
filesize ^ uint8(63) != 34
filesize ^ uint8(44) != 17
uint32(28) - 419186860 == 959764852
uint8(74) + 11 == 116
uint8(48) < 136
uint8(47) < 142
hash.crc32(63, 2) == 0x66715919
uint8(58) < 146
filesize ^ uint8(71) != 128
uint8(45) < 136
uint8(31) % 17 < 17
uint8(43) & 128 == 0
filesize ^ uint8(43) != 251
uint8(65) > 1
uint8(24) & 128 == 0
uint8(37) < 139
filesize ^ uint8(28) != 238
uint8(78) & 128 == 0
filesize ^ uint8(13) != 219
uint8(19) % 30 < 30
hash.sha256(14, 2) == "403d5f23d149670348b147a15eeb7010914701a7e99aad2e43f90cfa0325c76f"
filesize ^ uint8(53) != 243
uint8(81) & 128 == 0
uint8(46) % 28 < 28
filesize ^ uint8(65) != 215
filesize ^ uint8(0) != 41
uint8(84) < 129
uint8(60) & 128 == 0
uint8(20) > 1
uint8(2) % 28 < 28
uint8(58) % 14 < 14
uint8(34) & 128 == 0
uint8(21) & 128 == 0
uint8(84) % 18 < 18
uint8(74) % 10 < 10
uint8(9) < 151
uint8(73) % 23 < 23
filesize ^ uint8(39) != 49
uint8(4) % 17 < 17
filesize ^ uint8(60) != 142
filesize ^ uint8(69) != 30
uint8(30) > 6
uint8(65) & 128 == 0
uint8(39) % 11 < 11
uint8(13) % 27 < 27
uint8(17) % 11 < 11
uint8(56) % 26 < 26
uint8(29) < 157
uint8(57) & 128 == 0
filesize ^ uint8(29) != 37
uint8(77) > 5
filesize ^ uint8(16) != 144
uint8(37) & 128 == 0
filesize ^ uint8(25) != 47
uint8(67) & 128 == 0
filesize ^ uint8(24) != 94
uint8(68) < 138
uint8(57) < 138
filesize ^ uint8(27) != 43
filesize ^ uint8(30) != 18
filesize ^ uint8(59) != 13
uint8(27) % 26 < 26
uint8(56) > 8
uint8(69) & 128 == 0
uint8(18) & 128 == 0
uint8(64) < 154
uint8(76) & 128 == 0
uint8(71) % 28 < 28
filesize ^ uint8(84) != 3
filesize ^ uint8(38) != 84
uint8(32) < 140
filesize ^ uint8(42) != 91
uint8(40) > 15
uint8(27) > 23
uint8(6) % 12 < 12
uint8(10) % 10 < 10
uint8(8) % 21 < 21
filesize ^ uint8(18) != 234
uint8(68) & 128 == 0
uint8(7) < 131
uint8(72) < 134
uint8(16) > 25
uint8(12) % 23 < 23
uint8(41) % 27 < 27
uint8(1) % 17 < 17
uint8(26) > 31
hash.sha256(56, 2) == "593f2d04aab251f60c9e4b8bbc1e05a34e920980ec08351a18459b2bc7dbf2f6"
uint8(65) < 149
filesize ^ uint8(51) != 0
uint8(66) > 30
filesize ^ uint8(68) != 8
uint8(25) % 23 < 23
uint8(1) & 128 == 0
filesize ^ uint8(81) != 7
uint8(36) % 22 < 22
uint8(24) < 148
uint8(12) < 147
uint8(74) < 152
filesize ^ uint8(21) != 27
filesize ^ uint8(23) != 18
uint8(38) & 128 == 0
uint8(26) % 25 < 25
filesize ^ uint8(19) != 31
uint8(82) > 3
uint8(5) % 27 < 27
uint8(5) & 128 == 0
uint8(75) - 30 == 86
uint8(54) < 152
uint8(75) < 142
uint8(20) % 28 < 28
uint8(30) & 128 == 0
uint32(66) ^ 310886682 == 849718389
uint8(64) % 24 < 24
uint32(10) + 383041523 == 2448764514
uint8(79) & 128 == 0
filesize ^ uint8(59) != 194
uint8(61) & 128 == 0
uint8(70) < 139
uint8(77) & 128 == 0
uint8(13) & 128 == 0
uint8(21) < 138
filesize ^ uint8(46) != 186
uint8(43) % 26 < 26
uint8(61) < 160
filesize ^ uint8(34) != 39
uint8(6) > 6
uint8(35) & 128 == 0
uint8(23) < 141
filesize ^ uint8(82) != 32
filesize ^ uint8(48) != 29
uint8(59) & 128 == 0
uint8(40) % 19 < 19
filesize ^ uint8(39) != 18
filesize ^ uint8(45) != 146
uint8(80) & 128 == 0
uint8(16) < 134
uint8(74) > 1
uint8(23) & 128 == 0
uint8(32) & 128 == 0
filesize ^ uint8(47) != 119
filesize ^ uint8(63) != 135
uint8(64) > 27
uint32(37) + 367943707 == 1228527996
uint8(82) % 28 < 28
uint8(32) > 28
filesize ^ uint8(24) != 217
uint8(53) < 144
uint8(29) & 128 == 0
uint32(22) ^ 372102464 == 1879700858
uint8(52) % 23 < 23
filesize ^ uint8(76) != 88
filesize ^ uint8(55) != 17
uint8(26) & 128 == 0
uint8(51) > 7
uint8(12) > 19
filesize ^ uint8(14) != 99
filesize ^ uint8(37) != 141
filesize ^ uint8(14) != 161
uint8(45) % 17 < 17
uint8(33) % 25 < 25
filesize ^ uint8(67) != 55
filesize ^ uint8(53) != 19
uint8(30) < 131
uint8(0) & 128 == 0
uint8(66) & 128 == 0
uint8(41) > 5
uint8(71) & 128 == 0
uint8(29) % 12 < 12
uint8(4) < 139
uint8(77) < 154
filesize ^ uint8(12) != 116
uint8(39) > 7
uint8(75) & 128 == 0
uint8(78) > 24
uint8(69) > 25
uint8(2) + 11 == 119
uint8(15) < 156
filesize ^ uint8(69) != 241
filesize ^ uint8(35) != 18
filesize ^ uint8(17) != 208
hash.md5(0, 2) == "89484b14b36a8d5329426a3d944d2983"
filesize ^ uint8(4) != 23
uint8(15) % 16 < 16
filesize ^ uint8(75) != 35
uint32(46) - 412326611 == 1503714457
uint8(11) % 27 < 27
hash.crc32(78, 2) == 0x7cab8d64
uint8(83) & 128 == 0
filesize ^ uint8(26) != 161
uint8(49) % 13 < 13
filesize ^ uint8(18) != 33
uint8(6) < 155
uint8(41) < 140
filesize ^ uint8(68) != 135
filesize ^ uint8(9) != 5
uint8(9) & 128 == 0
filesize ^ uint8(36) != 95
uint8(7) > 18
filesize ^ uint8(23) != 242
uint8(62) < 146
uint8(49) & 128 == 0
uint8(62) & 128 == 0
uint8(4) & 128 == 0
filesize ^ uint8(58) != 12
uint8(72) & 128 == 0
uint8(18) > 13
filesize ^ uint8(42) != 1
uint8(59) % 23 < 23
uint8(53) & 128 == 0
filesize ^ uint8(78) != 163
uint8(60) > 14
uint8(47) % 18 < 18
uint8(79) > 31
uint8(22) < 152
filesize ^ uint8(64) != 50
filesize ^ uint8(19) != 222
uint8(81) < 131
uint8(7) - 15 == 82
filesize ^ uint8(51) != 204
uint8(28) > 27
uint32(70) + 349203301 == 2034162376
filesize ^ uint8(61) != 94
uint8(76) > 2
filesize ^ uint8(77) != 223
uint8(19) > 4
uint8(80) > 2
filesize ^ uint8(35) != 120
filesize ^ uint8(22) != 31
uint8(10) > 9
uint8(22) > 20
uint8(38) < 135
filesize ^ uint8(10) != 205
uint8(25) & 128 == 0
uint8(13) < 147
uint8(42) & 128 == 0
hash.md5(76, 2) == "f98ed07a4d5f50f7de1410d905f1477f"
filesize ^ uint8(48) != 99
filesize ^ uint8(16) != 7
uint8(11) < 154
filesize ^ uint8(76) != 30
uint8(30) % 15 < 15
filesize ^ uint8(74) != 193
filesize ^ uint8(52) != 22
filesize ^ uint8(36) != 6
uint8(22) % 22 < 22
uint8(44) & 128 == 0
uint8(50) & 128 == 0
filesize ^ uint8(25) != 224
uint8(15) > 26
filesize ^ uint8(60) != 43
uint8(22) & 128 == 0
uint8(82) & 128 == 0
uint32(80) - 473886976 == 69677856
uint8(75) > 30
uint8(32) % 17 < 17
filesize ^ uint8(15) != 27
uint8(67) % 16 < 16
uint8(23) > 2
uint8(62) % 13 < 13
uint8(34) < 138
filesize ^ uint8(31) != 32
uint8(72) % 14 < 14
filesize ^ uint8(81) != 242
filesize ^ uint8(54) != 141
uint8(63) & 128 == 0
uint8(0) < 129
uint8(70) % 21 < 21
uint8(8) & 128 == 0
uint8(61) > 12
uint8(24) > 22
uint8(53) % 23 < 23
uint8(46) & 128 == 0
uint8(24) % 26 < 26
uint32(3) ^ 298697263 == 2108416586
uint8(21) - 21 == 94
uint8(67) < 144
uint8(48) > 15
uint8(37) > 16
uint8(42) < 157
uint8(16) ^ 7 == 115
uint8(13) > 21
filesize ^ uint8(45) != 19
uint8(47) & 128 == 0
filesize ^ uint8(80) != 56
filesize ^ uint8(78) != 6
uint8(76) % 24 < 24
uint8(73) < 136
filesize ^ uint8(52) != 238
uint8(50) % 11 < 11
filesize ^ uint8(7) != 15
filesize ^ uint8(66) != 51
uint8(59) > 4
uint8(46) > 22
filesize ^ uint8(3) != 147
uint8(63) % 30 < 30
uint8(36) < 146
uint8(26) < 132
uint8(6) & 128 == 0
filesize ^ uint8(30) != 249
uint32(41) + 404880684 == 1699114335
filesize ^ uint8(5) != 243
uint8(70) & 128 == 0
uint8(9) % 22 < 22
uint8(59) < 141
filesize ^ uint8(79) != 104
filesize ^ uint8(5) != 43
filesize ^ uint8(72) != 219
uint8(52) > 25
uint8(74) & 128 == 0
uint8(28) < 160
uint8(51) & 128 == 0
hash.md5(50, 2) == "657dae0913ee12be6fb2a6f687aae1c7"
uint8(83) > 16
uint8(31) > 7
uint8(84) & 128 == 0
filesize ^ uint8(46) != 18
uint8(2) > 20
uint8(5) < 158
filesize ^ uint8(32) != 30
filesize ^ uint8(50) != 219
uint8(26) - 7 == 25
uint8(53) > 24
uint8(77) % 24 < 24
uint8(3) % 13 < 13
filesize ^ uint8(9) != 164
filesize ^ uint8(80) != 236
uint8(65) % 22 < 22
filesize ^ uint8(84) != 231
filesize ^ uint8(49) != 10
uint8(67) > 27
uint8(34) % 19 < 19
uint8(64) & 128 == 0
filesize ^ uint8(27) != 244
uint8(12) & 128 == 0
uint8(51) < 139
uint8(35) % 15 < 15
uint8(5) > 14
filesize ^ uint8(34) != 115
filesize ^ uint8(38) != 8
filesize ^ uint8(72) != 37
uint8(20) & 128 == 0
uint8(17) < 150
filesize ^ uint8(70) != 41
uint8(66) % 16 < 16
uint8(17) & 128 == 0
uint8(19) & 128 == 0
filesize ^ uint8(33) != 157
uint8(21) > 7
uint8(58) & 128 == 0
uint8(71) < 130
uint8(41) & 128 == 0
uint8(57) > 11
hash.md5(32, 2) == "738a656e8e8ec272ca17cd51e12f558b"
filesize ^ uint8(8) != 2
filesize ^ uint8(57) != 186
uint8(11) & 128 == 0
uint8(2) < 147
uint8(23) % 16 < 16
uint8(78) < 141
uint8(38) > 18
filesize ^ uint8(41) != 233
uint8(18) < 137
uint8(40) & 128 == 0
filesize ^ uint8(21) != 188
filesize ^ uint8(57) != 14
filesize ^ uint8(4) != 253
uint8(14) < 153
uint8(31) & 128 == 0
uint8(81) > 11
uint8(2) & 128 == 0
filesize ^ uint8(22) != 191
uint8(44) > 5
uint8(84) + 3 == 128
uint8(20) < 135
filesize ^ uint8(73) != 61
filesize ^ uint8(26) != 44
uint8(1) < 158
filesize ^ uint8(29) != 158
uint8(49) < 129
filesize ^ uint8(64) != 158
uint8(25) < 154
uint8(63) < 129
uint8(84) > 26
uint8(39) & 128 == 0
uint8(25) > 27
uint8(49) > 27
uint8(9) > 23
filesize ^ uint8(7) != 221
uint8(50) < 138
uint8(76) < 156
filesize ^ uint8(61) != 239
uint8(57) % 27 < 27
filesize ^ uint8(8) != 107
uint8(79) < 146
filesize ^ uint8(40) != 49
uint8(0) > 30
uint8(45) > 17
uint8(16) % 31 < 31
filesize ^ uint8(1) != 232
filesize ^ uint8(56) != 22
uint8(42) > 3
uint8(52) & 128 == 0
uint8(69) % 30 < 30
uint8(55) < 153
filesize ^ uint8(41) != 74
filesize ^ uint8(1) != 0
filesize ^ uint8(44) != 96
filesize ^ uint8(58) != 77
uint8(34) > 18
uint8(8) > 3
"""

result = solve_yara_conditions(conds)
print(result)
