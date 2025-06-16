subroutine kmeans(n, k, r, x, m, th, maxit, c, l)
  implicit none
  interface
    real function dE00(a, b)
      real, intent(in), dimension(3) :: a, b
    end function
  end interface
  integer, intent(in) :: n, k, r
  real, intent(in) :: x(n, r)
  real, intent(in) :: m(k, r)
  real, optional, intent(in) :: th
  integer, optional, intent(in) :: maxit
  real, intent(out) :: c(k, r)
  integer, intent(out) :: l(n)
  real :: d(k)
  integer :: i, j, z, indx
  logical :: alt, mask(n)

  c = m
  do i = 1, maxit
    alt = .FALSE.
    do concurrent(j = 1:n)
      do concurrent(z = 1:k)
        d(z) = dE00(x(j, :), m(z, :))
      end do
      if(minval(d) < th) then
        indx = minloc(d, dim=1)
      else
        indx = 0
      end if
      if(l(j) /= indx) then
        l(j) = indx
        alt = .TRUE.
      end if
    end do
    if(.not. alt) exit
    do concurrent(j = 1:k)
      mask = l == j
      do concurrent(z = 1:r)
        c(j, z) = sum(x(:, z), mask=mask) / count(mask)
      end do
    end do
    if(i == maxit) error stop
  end do
end subroutine

real function dE00(a, b) result(d)
  implicit none
  interface
    real function rad(deg)
      real, intent(in) :: deg
    end function
  end interface
  ! real, parameter :: kL = 1., kC = 1., kH = 1.
  real, intent(in), dimension(3) :: a, b
  real :: c1, c2, c, g, a1, a2, cs1, cs2, h1, h2,&
    dl, dc, dh, ls, cs, hs, t, theta, rc, sl, sc,&
    sh, rt

  c1 = norm2(a(2:))
  c2 = norm2(b(2:))
  c = .5 * (c1 + c2)
  g = .5 * (1. - sqrt(c**7 / (c**7 + 25.**7)))
  a1 = (1. + g) * a(2)
  a2 = (1. + g) * b(2)
  cs1 = sqrt(a1**2 + a(3))
  cs2 = sqrt(a2**2 + b(3))
  h1 = 0
  h2 = 0
  if(a(3) /= 0 .or. a1 /= 0) h1 = atan2(a(3), a1)
  if(b(3) /= 0 .or. a2 /= 0) h2 = atan2(b(3), a2)

  dl = b(1) - a(1)
  dc = cs2 - cs1
  if(cs1 * cs2 == 0) then
    dh = 0
  else
    dh = h2 - h1
    if(dh > rad(180.)) then
      dh = dh - rad(360.)
    else if(dh < rad(180.)) then
      dh = dh + rad(360.)
    end if
  end if
  dh = 2. * sqrt(cs1 * cs2) * sin(.5 * dh)

  ls = .5 * (a(1) + b(1))
  cs = .5 * (cs1 + cs2)
  hs = h1 + h2
  if(cs1 * cs2 /= 0) then
    if(abs(h1 - h2) > rad(180.)) then
      if(hs < rad(360.)) then
        hs = hs + rad(360.)
      else
        hs = hs - rad(360.)
      endif
    end if
    hs = .5 * hs
  end if
  t = 1. - .17 * cos(hs - rad(30.)) + .24 * cos(2. * hs)&
    + .32 * cos(3. * hs + rad(6.)) - .2 * cos(4. * hs - rad(63.))
  theta = 30. * exp(-((hs - rad(275.)) / 25.)**2)
  rc = 2. * sqrt(cs**7 / (cs**7 + 25.**7))
  sl = 1. + .015 * (ls - 50.)**2 / sqrt(20. + (ls - 50.)**2)
  sc = 1. + .045 * cs
  sh = 1. + .015 * cs * t
  rt = -sin(2. * theta) * rc
  d = sqrt((dl/sl)**2 + (dc/sc)**2 + (dh/sh)**2 + rt*(dc/sc)*(dh/sh))
end function

real function rad(deg)
  real, parameter :: pi = 4. * atan(1.)
  real, intent(in) :: deg

  rad = pi * deg / 180.
end function
