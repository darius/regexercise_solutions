// star_thompsonlike_lowlevel.py ported to C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { loud = 0 };

static void error(const char *plaint) {
    fprintf(stderr, "%s\n", plaint);
    exit(1);
}

enum { max_insns = 8192, accept = 0 };
enum { op_accept, op_eat, op_fork, op_loop };
static int           ninsns;
static unsigned char accepts[max_insns], ops[max_insns];
static int           arg1[max_insns], arg2[max_insns];

static const char* names[] = {
    "win", "eat", "fork", "loop",
};

static void dump1(int pc) {
    printf("%c %2u: %-4s ", accepts[pc] ? '*' : ' ', pc, names[ops[pc]]);
    printf(pc == accept ? "\n" : ops[pc] == op_eat ? "'%c' %d\n" : "%d %d\n",
           arg1[pc], arg2[pc]);
}

static void dump(void) {
    for (int pc = ninsns-1; 0 <= pc; --pc)
        dump1(pc);
}

static unsigned char occupied[max_insns];

static void after(char ch, int start, int end, int **next_states) {
    while (start != end) {
        int r = arg1[start];
        int s = arg2[start];
        switch (ops[start]) {
        case op_eat:
            if (r == ch && !occupied[s]) {
                *(*next_states)++ = s;
                occupied[s] = 1;
            }
            return;
        case op_fork:
            after(ch, r, end, next_states);
            start = s;
            break;
        case op_loop:
            after(ch, r, start, next_states);
            start = s;
            break;
        default:
            error("Can't happen");
        }
    }
}

static int run(int start, const char *input) {
    if (accepts[start])
        return 1;

    static int states0[max_insns], states1[max_insns];
    int *cur_start = states0, *cur_end = cur_start;
    int *next_start = states1, *next_end = next_start;
    *cur_end++ = start;
    memset(occupied, 0, ninsns); // N.B. we could avoid this by always
                                 // finishing the next_start..next_end
                                 // loop below

    for (; *input; ++input) {
        for (int *state = cur_start; state < cur_end; ++state)
            after(*input, *state, accept, &next_end);
        for (int *state = next_start; state < next_end; ++state) {
            if (accepts[*state])
                return 1;
            occupied[*state] = 0;
        }
        {
            int *t = cur_start;
            cur_start = next_start, cur_end = next_end;
            next_start = next_end = t;
        }
    }
    return 0;
}

static int emit(unsigned char op, int r, int s, unsigned char accepting) {
    if (max_insns <= ninsns) error("Pattern too long");
    ops[ninsns] = op, arg1[ninsns] = r, arg2[ninsns] = s;
    accepts[ninsns] = accepting;
    return ninsns++;
}

static const char *pattern, *pp; // start, current parsing position

static int eat(char c) {
    return pattern < pp && pp[-1] == c ? (--pp, 1) : 0;
}

static int parsing(int precedence, int state) {
    int rhs;
    if (pattern == pp || pp[-1] == '(' || pp[-1] == '|')
        rhs = state;
    else if (eat(')')) {
        rhs = parsing(0, state);
        if (!eat('(')) error("Mismatched ')'");
    }
    else if (eat('*')) {
        rhs = emit(op_loop, 0, state, accepts[state]); // (0 is a placeholder...
        arg1[rhs] = parsing(6, rhs);                   // ...filled in here.)
    }
    else
        rhs = emit(op_eat, *--pp, state, 0);
    while (pattern < pp && pp[-1] != '(') {
        int prec = pp[-1] == '|' ? 3 : 5;
        if (prec <= precedence) break;
        if (eat('|')) {
            int rhs2 = parsing(prec, state);
            rhs = emit(op_fork, rhs, rhs2, accepts[rhs] || accepts[rhs2]);
        } else
            rhs = parsing(prec, rhs);
    }
    return rhs;
}

static int parse(const char *string) {
    pattern = string; pp = pattern + strlen(pattern);
    ninsns = 0;
    int state = parsing(0, emit(op_accept, 0, 0, 1));
    if (pattern != pp) error("Bad pattern");
    return state;
}

int main(int argc, char **argv) {
    int matched = 0;
    if (argc != 2) error("Usage: grep pattern");
    int start_state = parse(argv[1]);
    if (loud) {
        printf("start: %u\n", start_state);
        dump();
    }
    char line[9999];
    while (fgets(line, sizeof line, stdin)) {
        line[strlen(line) - 1] = '\0';
        if (run(start_state, line)) {
            puts(line);
            matched = 1;
        }
    }
    return matched ? 0 : 1;
}
