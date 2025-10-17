#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef enum {
    CON_EQ, CON_NEQ, CON_LT, CON_GT, CON_LE, CON_GE, CON_AND, CON_OR, CON_XOR, CON_ADD, CON_SUB, CON_MOD
} ConstraintOp;

typedef struct {
    int idx;           // index in arr
    ConstraintOp op;   // operation
    int value;         // value to compare
    int extra;         // extra value if needed (e.g., for XOR, ADD, etc.)
} Constraint;

#define MAX_CONSTRAINTS 256

Constraint constraints[MAX_CONSTRAINTS];
int constraint_count = 0;

// Example: parse a constraint and add to array
void add_constraint(int idx, ConstraintOp op, int value, int extra) {
    constraints[constraint_count].idx = idx;
    constraints[constraint_count].op = op;
    constraints[constraint_count].value = value;
    constraints[constraint_count].extra = extra;
    constraint_count++;
}

// Example: check all constraints
int check_constraints(const uint8_t arr[85]) {
    for (int i = 0; i < constraint_count; i++) {
        int idx = constraints[i].idx;
        int val = arr[idx];
        switch (constraints[i].op) {
            case CON_EQ:   if (val != constraints[i].value) return 0; break;
            case CON_NEQ:  if (val == constraints[i].value) return 0; break;
            case CON_LT:   if (val >= constraints[i].value) return 0; break;
            case CON_GT:   if (val <= constraints[i].value) return 0; break;
            case CON_LE:   if (val > constraints[i].value) return 0; break;
            case CON_GE:   if (val < constraints[i].value) return 0; break;
            case CON_AND:  if ((val & constraints[i].extra) != constraints[i].value) return 0; break;
            case CON_OR:   if ((val | constraints[i].extra) != constraints[i].value) return 0; break;
            case CON_XOR:  if ((val ^ constraints[i].extra) != constraints[i].value) return 0; break;
            case CON_ADD:  if ((val + constraints[i].extra) != constraints[i].value) return 0; break;
            case CON_SUB:  if ((val - constraints[i].extra) != constraints[i].value) return 0; break;
            case CON_MOD:  if ((val % constraints[i].extra) >= constraints[i].value) return 0; break;
        }
    }
    return 1;
}

// You can now add constraints programmatically
// add_constraint(55, CON_AND, 0, 128); // arr[55] & 128 == 0
// add_constraint(58, CON_ADD, 122, 25); // arr[58] + 25 == 122
