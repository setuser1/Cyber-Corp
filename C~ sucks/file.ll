; ModuleID = "module"
target triple = "x86_64-pc-windows-msvc"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", i32* %".2", ...)

@"fmt_int" = constant [4 x i8] c"%d\0a\00"
@"fmt_in" = constant [3 x i8] c"%d\00"
define void @"print"()
{
entry:
  %".2" = getelementptr [27 x i8], [27 x i8]* @"fmt_str_7099849943388741752", i32 0, i32 0
  %".3" = call i32 (i8*, ...) @"printf"(i8* %".2")
  ret void
}

define i32 @"main"()
{
entry:
  %"x" = alloca i32
  %"f" = alloca i32
  %"d" = alloca float
  %"a" = alloca double
  %"new" = alloca i32
  %"list" = alloca i8, i32 10
  %".2" = getelementptr [17 x i8], [17 x i8]* @"fmt_str_9153114359808808135", i32 0, i32 0
  %".3" = call i32 (i8*, ...) @"printf"(i8* %".2")
  store i32 0, i32* %"x"
  br label %"loop"
loop:
  %"load_x" = load i32, i32* %"x"
  %".6" = icmp slt i32 %"load_x", 5
  br i1 %".6", label %"body", label %"after"
body:
  %"load_x.1" = load i32, i32* %"x"
  %".8" = getelementptr [3 x i8], [3 x i8]* @"fmt_str_7558924934987663007", i32 0, i32 0
  %".9" = call i32 (i8*, ...) @"printf"(i8* %".8", i32 %"load_x.1")
  %".10" = getelementptr [2 x i8], [2 x i8]* @"fmt_str_3698182564054797699", i32 0, i32 0
  %".11" = call i32 (i8*, ...) @"printf"(i8* %".10")
  %"load_x.2" = load i32, i32* %"x"
  %"add_x" = add i32 %"load_x.2", 1
  store i32 %"add_x", i32* %"x"
  br label %"loop"
after:
  store i32 9, i32* %"f"
  store float 0x3ff0000000000000, float* %"d"
  store double 0x4014051eb851eb85, double* %"a"
  %"load_x.3" = load i32, i32* %"x"
  %"load_f" = load i32, i32* %"f"
  %"call_func" = call i32 @"func"(i32 %"load_x.3", i32 %"load_f")
  store i32 %"call_func", i32* %"new"
  %"load_new" = load i32, i32* %"new"
  %".18" = getelementptr [4 x i8], [4 x i8]* @"fmt_str_4412372678270838092", i32 0, i32 0
  %".19" = call i32 (i8*, ...) @"printf"(i8* %".18", i32 %"load_new")
  call void @"print"()
  %".21" = getelementptr i8, i8* %"list", i32 0
  store i8 104, i8* %".21"
  %".23" = getelementptr i8, i8* %"list", i32 1
  store i8 101, i8* %".23"
  %".25" = getelementptr i8, i8* %"list", i32 2
  store i8 108, i8* %".25"
  %".27" = getelementptr i8, i8* %"list", i32 3
  store i8 108, i8* %".27"
  %".29" = getelementptr i8, i8* %"list", i32 4
  store i8 111, i8* %".29"
  %".31" = getelementptr i8, i8* %"list", i32 5
  store i8 0, i8* %".31"
  %".33" = getelementptr [3 x i8], [3 x i8]* @"fmt_str_3158755294970576787", i32 0, i32 0
  %".34" = call i32 (i8*, ...) @"printf"(i8* %".33", i8* %"list")
  ret i32 0
}

define i32 @"func"(i32 %".1", i32 %".2")
{
entry:
  %"add" = alloca i32
  %"a" = alloca i32
  store i32 %".1", i32* %"a"
  %"b" = alloca i32
  store i32 %".2", i32* %"b"
  %"load_a" = load i32, i32* %"a"
  %"load_b" = load i32, i32* %"b"
  %"add_add" = add i32 %"load_a", %"load_b"
  store i32 %"add_add", i32* %"add"
  %"load_add" = load i32, i32* %"add"
  ret i32 %"load_add"
}

@"fmt_str_7099849943388741752" = constant [27 x i8] c"\0aThis is a void basically\0a\00"
@"fmt_str_9153114359808808135" = constant [17 x i8] c"Print statement\0a\00"
@"fmt_str_7558924934987663007" = constant [3 x i8] c"%d\00"
@"fmt_str_3698182564054797699" = constant [2 x i8] c" \00"
@"fmt_str_4412372678270838092" = constant [4 x i8] c"\0a%d\00"
@"fmt_str_3158755294970576787" = constant [3 x i8] c"%s\00"