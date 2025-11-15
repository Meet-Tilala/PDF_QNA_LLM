# XV6 Feature Implementation: The "Welcoming Fork"

## Objective (Part C)

The goal is to modify the behavior of the `fork()` system call to allow a parent process to specify a user-space "welcome" function where a new child process will begin execution. After completing this function, the child must invoke a new system call, `welcomeDone()`, to resume execution immediately after the original `fork()` call, as a standard child process would.

This is achieved by manipulating the child's **Trap Frame EIP (Instruction Pointer)**.

---

## Step-by-Step Kernel Modifications

### 1\. Update Process Structure (`kernel/proc.h`)

We need three new fields in `struct proc` to manage the state and addresses for the welcomed child.

```c
// in kernel/proc.h, inside struct proc
uint welcome_fn;        // Address set by parent via welcomeFunction()
uint saved_eip;         // Child's original post-fork return EIP
int started_welcome;    // Flag: 1 if child must call welcomeDone()
```

### 2\. Initialize Fields (`kernel/proc.c`: `allocproc`)

Ensure the new fields are initialized to zero when a process structure is allocated.

```c
// in kernel/proc.c, inside allocproc()

// ... (other initialization)
p->welcome_fn = 0;
p->saved_eip = 0;
p->started_welcome = 0;
// ...
```

### 3\. Implement System Calls (`kernel/proc.c`)

The new syscalls handle setting the welcome address and restoring the instruction pointer.

#### `sys_welcomeFunction(addr)`

The parent calls this to set the `welcome_fn` for its future children.

```c
// in kernel/proc.c
int sys_welcomeFunction(void)
{
    uint addr;
    // Retrieve the function address argument
    if(argint(0, (int*)&addr) < 0)
        return -1;

    // Set the welcome function address for *this* process
    myproc()->welcome_fn = addr;
    return 0;
}
```

#### `sys_welcomeDone()`

The child calls this at the end of the welcome function to resume normal execution.

```c
// in kernel/proc.c
int sys_welcomeDone(void)
{
    struct proc *p = myproc();

    if(!p->started_welcome){
        return -1; // Not a welcomed child, ignore or error
    }

    // CRITICAL STEP: Restore the saved EIP
    p->tf->eip = p->saved_eip;

    // Clear state flags
    p->started_welcome = 0;
    p->saved_eip = 0;

    return 0;
}
```

### 4\. Modify Fork Logic (`kernel/proc.c`: `fork`)

After the child process (`np`) copies the parent's trap frame (`*np->tf = *curproc->tf;`), we save the original EIP and conditionally redirect execution.

```c
// in kernel/proc.c, inside fork()

// ... after *np->tf = *curproc->tf; ...

// 1. Always save the original return EIP
np->saved_eip = np->tf->eip;

if(curproc->welcome_fn != 0){
    // 2. Redirect the child's EIP to the welcome function address
    np->tf->eip = curproc->welcome_fn;
    // 3. Set the flag for welcomeDone()
    np->started_welcome = 1;
} else {
    // 4. Normal execution path
    np->started_welcome = 0;
}

// ... (continue to set child RUNNABLE)
```

---

## 🔌 System Call Wiring

### 5\. Numbering and Prototypes

| File               | Change                                                           | Description                              |
| :----------------- | :--------------------------------------------------------------- | :--------------------------------------- |
| `syscall.h`        | `#define SYS_welcomeFunction 45`<br>`#define SYS_welcomeDone 46` | Assign next available syscall numbers.   |
| `kernel/defs.h`    | `int sys_welcomeFunction(void);`<br>`int sys_welcomeDone(void);` | Add kernel function prototypes.          |
| `kernel/syscall.c` | Add extern declarations and map in `syscalls[]` array.           | Links the number to the kernel function. |

### 6\. User-Space Stubs

| File          | Change                                                       | Description                                           |
| :------------ | :----------------------------------------------------------- | :---------------------------------------------------- |
| `usys.S`      | `SYSCALL(welcomeFunction)`<br>`SYSCALL(welcomeDone)`         | Creates the assembly wrapper to initiate the syscall. |
| `user/user.h` | `int welcomeFunction(int addr);`<br>`int welcomeDone(void);` | Provides user-level function declarations.            |

---

## Test Program (`user/test_welcome.c`)

This program demonstrates that the first child follows the normal path, while the second child is successfully hijacked and restored.

```c
#include "types.h"
#include "stat.h"
#include "user.h"

void welcome(void)
{
    printf(1, "Child %d: running welcome()\n", getpid());

    // Call the syscall to restore the original EIP and resume post-fork code
    welcomeDone();

    printf(1, "Child %d: back after welcomeDone, returning from fork\n", getpid());
    exit();
}

int main(void)
{
    int pid;

    // --- Test 1: Normal Fork ---
    pid = fork();
    if(pid == 0){
        printf(1, "Child1 %d: normal child, no welcome\n", getpid());
        exit();
    }

    // Parent sets welcome function
    welcomeFunction((int)welcome);

    // --- Test 2: Welcomed Fork ---
    pid = fork();
    if(pid == 0){
        // Child 2's EIP is set to welcome(), so execution starts there.
        // It should never reach this loop because welcome() calls exit().
        while(1) sleep(1);
    }

    // Parent waits for both children
    wait();
    wait();

    printf(1, "Parent %d: All children done.\n", getpid());
    exit();
}
```

### Expected Output

(Order and PIDs may vary, but the flow is critical)

```
Child1 4: normal child, no welcome
Child 5: running welcome()
Child 5: back after welcomeDone, returning from fork
Parent 3: All children done.
```

---

## Build and Execution

1.  **Update `Makefile`:** Add `_test_welcome` to the `UPROGS` list.
2.  **Clean & Build:**
    ```bash
    make clean
    make qemu
    ```
3.  **Run Test:**
    ```bash
    $ test_welcome
    ```
