
class Backtracking:
    def __init__(self, csp):
        self.csp = csp
        unasgn_vars = list()
        self.nPrunings  = 0
        self.nDecisions = 0
    
    def restoreValues(self,prunings):
        for var, val in prunings:
            var.unprune_value(val)
    
    def restore_all_variable_domains(self):
        for row in self.csp.vars:
            for var in row:
                if var.is_assigned():
                    var.unassign()
                var.restore_curdom()
    
    def restoreUnasgnVar(self, var):
        self.unasgn_vars.append(var)
    
    def clear_stats(self):
        self.nDecisions = 0
        self.nPrunings = 0
        self.runtime = 0

    def print_stats(self):
        print("Search made {} variable assignments and pruned {} variable values".format(
            self.nDecisions, self.nPrunings))
    
    def bt_search(self, propagator, var_ord=None,val_ord=None):
        self.restore_all_variable_domains()
        
        self.unasgn_vars = []
        for row in self.csp.vars:
            for var in row:
                if not var.is_assigned():
                    self.unasgn_vars.append(var)
        print(self.unasgn_vars)
        status, prunings = propagator(self.csp) #initial propagate no assigned variables.
        self.nPrunings = self.nPrunings + len(prunings)

        if status == False:
            print("CSP detected contradiction at root")
        else:
            status = self.bt_recurse(propagator, var_ord, val_ord, 1) 

        self.restoreValues(prunings)
        if status == False:
            print("CSP unsolved. Has no solutions")
        if status == True:
            print("CSP solved. ")
            self.csp.print_soln()
        print("bt_search finished")
        self.print_stats()
    
    def bt_recurse(self, propagator, var_ord, val_ord, level):
        if not self.unasgn_vars:
            #all variables assigned
            return True
        else:
            ##Figure out which variable to assign,
            ##Then remove it from the list of unassigned vars
            if var_ord:
              var = var_ord(self.csp)
            else:
              var = self.unasgn_vars[0]
            self.unasgn_vars.remove(var) 

            if val_ord:
              value_order = val_ord(self.csp,var)
            else:
              value_order = var.cur_domain()

            for val in value_order:
                var.assign(val)
                self.nDecisions = self.nDecisions+1

                status, prunings = propagator(self.csp, var)
                self.nPrunings = self.nPrunings + len(prunings)

            if status:
                    if self.bt_recurse(propagator, var_ord, val_ord, level+1):
                        return True
            self.restoreValues(prunings)
            var.unassign()

            self.restoreUnasgnVar(var)
            return False
        
def prop_BT(csp, newVar=None):
    '''Do plain backtracking propagation. That is, do no
    propagation at all. Just check fully instantiated constraints'''

    if not newVar:
        return True, []
    for c in csp.get_cons_with_var(newVar):
        if c.get_n_unasgn() == 0:
            vals = []
            vars = c.get_scope()
            for var in vars:
                vals.append(var.get_assigned_value())
            if not c.check(vals):
                return False, []
    return True, []