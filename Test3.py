import pyopencl as ocl
import numpy as np
import os
import sys

a = np.random.rand(3 * 3)
print a
a += 0.5
print a
print a.reshape(3, 3).astype(np.int32)
sys.exit(0)

clKernel = """
void mMult(__global int *a, __global int *b, __global int *c, int n){
    for(int i = 0;i < n;i++){
        for(int j = 0;j < n;j++){
            int d = 0;
            for(int k = 0;k < n;k++){
                d += a[i * n + k] * b[k * n + j];
            }
            c[i * n + j] = d;
        }
    }
}

__kernel void matrixMult(__global const int *a, __global const int *b, __global int *c, __global int *n, __global int *size){
    int gid = get_global_id(0);
    if(gid < size[0]){
        for(int i = 0;i < n[0];i++){
            __global float *mA = &a[n[0] * n[0] * gid];
            __global float *mB = &b[n[0] * n[0] * gid];
            __global float *mC = &c[n[0] * n[0] * gid];
            mMult(mA, mB, mC, n[0]);
        }
    }
}"""

os.environ["PYOPENCL_COMPILER_OUTPUT"] = "1"

ctx = ocl.create_some_context(interactive=True)
queue = ocl.CommandQueue(ctx)

mf = ocl.mem_flags

repeat = 10
n = 3

a = [100 * np.random.rand(n**2) - 50 for i in range(0, repeat)]
b = [100 * np.random.rand(n**2) - 50 for i in range(0, repeat)]

for i in range(0, repeat):
    for j in range(0, n**2):
        a[i][j] += 0.5
        b[i][j] += 0.5

#a_np = np.asarray(a, dtype=np.int32)
#b_np = np.asarray(b, dtype=np.int32)
a_np = np.zeros(repeat * n ** 2, dtype=np.int32)
b_np = np.zeros(repeat * n ** 2, dtype=np.int32)
for i in range(0, repeat):
    a_np[n**2 * i:n**2 * i + n**2] = a[i]
    b_np[n**2 * i:n**2 * i + n**2] = b[i]

a_g = ocl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)
b_g = ocl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b_np)
n_g = ocl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=np.array([n], dtype=np.int32))
size_g = ocl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=np.array([repeat], dtype=np.int32))

prg = ocl.Program(ctx, clKernel).build()

res_g = ocl.Buffer(ctx, mf.WRITE_ONLY, a_np.size * a_np.itemsize)
prg.matrixMult(queue, (repeat,), None, a_g, b_g, res_g, n_g, size_g)

res_np = np.empty_like(a_np, dtype=np.int32)
ocl.enqueue_copy(queue, res_np, res_g)

res = []
for i in range(0, repeat):
    res.append(np.matrix(np.array(res_np[i * n**2:i * n**2 + n**2]).reshape((n, n))))

aM = [None] * repeat
bM = [None] * repeat
cM = [None] * repeat
for i in range(0, repeat):
    aM[i] = np.matrix(a_np[n**2 * i:n**2 * i + n**2].reshape((n, n)))
    bM[i] = np.matrix(b_np[n**2 * i:n**2 * i + n**2].reshape((n, n)))
    cM[i] = aM[i] * bM[i]

print res
print cM

d = [None] * repeat
for i in range(0, 10):
    d[i] = res[i] == cM[i]
print d