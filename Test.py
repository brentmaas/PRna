"""import sys
import numpy as np

a = np.random.rand(6).reshape((2, 3))

b = np.zeros(20).reshape((4, 5))

print a
print b

for x in range(0, 2):
    for y in range(0, 3):
        b[x + 1][y + 1] = a[x][y]

print b

sys.exit(0)

a = np.random.rand(6).reshape((2, 3))
a += 0.5
print a
a = a.astype(np.int32)
b = a.copy().astype(np.bool8)

print a
print b

sys.exit(0)"""

import sys

sys.exit(0)

import pyopencl as ocl
import numpy as np

import os

os.environ["PYOPENCL_COMPILER_OUTPUT"] = "1"

ctx = ocl.create_some_context(interactive=True)
queue = ocl.CommandQueue(ctx)

mf = ocl.mem_flags

a_np = np.random.rand(20).reshape((4, 5)).astype(np.float32)
a_np += 0.5
a_np = a_np.astype(np.int32).astype(np.float32)

print a_np

a_np = a_np.reshape(20)

a_g = ocl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a_np)

prg = ocl.Program(ctx, """
__kernel void sum(
    __global const float *a_g, __global float *res_g)
{
  int gid = get_global_id(0);
  int n = a_g[gid-5];
  n = n + a_g[gid+5];
  if(gid % 5 == 0)
  {
      n = n + 10;
  }
  res_g[gid] = n;
}
""").build()

res_g = ocl.Buffer(ctx, mf.WRITE_ONLY, (a_np.size - 0) * a_np.itemsize)
prg.sum(queue, a_np.shape, None, a_g, res_g)

res_np = np.empty_like(a_np)
ocl.enqueue_copy(queue, res_np, res_g)

res_np = res_np.reshape((4, 5))

print
print res_np