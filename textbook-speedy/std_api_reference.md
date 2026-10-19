# Coral Standard Library, Complete API Reference

This document catalogues every `pub` export of the Coral standard library and the
core/platform support modules it builds on. It is generated from the actual source
tree under `lib/` and reflects the current dialect.

- **Sources of truth:** `lib/core/**`, `lib/platform/**`, and the per-target
  `lib/std/x86_64/<target>/**` trees. The primary target documented here is
  **`x86_64/linux`**; `lib/std/x86_64/windows/**` mirrors it with platform
  differences (noted where relevant).
- **Top-level manifest:** `lib/std/lib.crl` re-exports the submodules; the
  per-target manifest is `lib/std/x86_64/linux/lib.crl`.
- **Signature syntax:** `RetType name(params)`. Tuple *types* are spelled
  `struct(T, T)` (never `(T, T)`). Generics are `<T>`, `<T, U>`, `<T, usize N>`,
  or `<comptime N>`; there are no generic bounds and no trait composition.
- **Visibility:** the dialect has no per-method `pub`; every member declared in a
  `pub struct`/`pub variant`/`pub enum`/`pub extend` is public. Members named with
  a leading `_` are internal helpers, listed here for completeness but not
  intended for direct use.
- **`@drop`:** `@drop` is an inbuilt trait. Types that own heap memory provide an
  `extend <T> : @drop { void drop() }` block wiring their `dispose()` into the
  language's automatic cleanup.

---

## 0. Prelude and module layout

### Prelude
The following are merged into every translation unit automatically:

```
std::io::ios          // print / println / eprint / eprintln / readLine / ...
std::text::string     // String
std::option           // Option<T>
std::result           // Result<T, E>
std::vec              // Vec<T>
std::collections::arr // Arr<T, N>
core::str             // `str` methods
```

### Module tree (`lib/std/lib.crl`)
```
pub mod collections = import collections;
pub mod concurrent  = import concurrent;
pub mod crypto      = import crypto;
pub mod data        = import data;
pub mod fmt         = import fmt;
pub mod io          = import io;
pub mod math        = import math;
pub mod memory      = import memory;
pub mod parser      = import parser;
pub mod text        = import text;

pub mod option    = import data::option;
pub mod result    = import data::result;
pub mod time      = import time;
pub mod duration  = import duration;
pub mod vec       = import collections::vec;
pub mod arr       = import collections::arr;
pub mod mman      = import memory::mman;
pub mod allocator = import memory::allocators;
```

### Per-target manifest (`lib/std/x86_64/linux/lib.crl`)
```
pub mod memory    = import memory;
pub mod mman      = import memory::mman;
pub mod allocator = import memory::allocators;
pub mod io        = import io;
pub mod concurrent = import concurrent;
pub mod crypto    = import crypto;
pub mod math      = import math;
pub mod vec       = import collections::vec;
pub mod option    = import data::option;
pub mod result    = import data::result;
pub mod time      = import time;
pub mod duration  = import duration;
pub mod intrinsics = import memory::intrinsics;
```

Submodule manifests:
```
collections/lib.crl : arr vec bitset cache deque hashmap iter linkedlist map
                      priorityqueue queue ringbuf set sort tree trie unordered_map
text/lib.crl        : ascii crlb regex string strutil uri utf8
data/lib.crl        : option result
math/lib.crl        : complex math matrix random vector
io/lib.crl          : bio cmd env fios fs ios log net path process temp term
memory/lib.crl      : mman allocators intrinsics pool shared_ptr smart_ptr
memory/allocators/lib.crl : allocator tlsf mimalloc
concurrent/lib.crl  : async mutex rwlock semaphore signal thread threadpool
crypto/lib.crl      : aes base64 bloom crc hash hex hmac sha256
parser/lib.crl      : csv ini json toml uuid xml
fmt/lib.crl         : fmt
misc/lib.crl        : erased cast
testing/lib.crl     : test
core/lib.crl        : cchar limits char_util
platform/lib.crl    : libc win32
```

> **Known inconsistencies in the manifests (not fixed here):**
> - `text/lib.crl` declares `pub mod crlb = import crlb;`, but no
>   `text/crlb.crl` exists, this import is dangling.
> - `parser/crlb.crl` exists but is **not** re-exported by `parser/lib.crl`.
> - `std/lib.crl` does **not** re-export `misc` or `testing`; import those paths
>   directly.

---

## core

### 1. `core::cchar`, C character type

```coral
pub distinct cchar = flag (arch)
{
    x86_64 => { i8 },
    else   => { u8 }
}
```
A `cchar` is a `char`-like C character whose signedness depends on the target
architecture (signed `i8` on x86_64, unsigned `u8` elsewhere).

### 2. `core::limits`, Integer and float limits

```coral
pub const INT64_MIN = -9223372036854775808;
pub const INT64_MAX =  9223372036854775807;
pub const INT32_MIN = -2147483648;
pub const INT32_MAX =  2147483647;
pub const INT16_MIN = -32768;
pub const INT16_MAX =  32767;
pub const INT8_MIN  = -128;
pub const INT8_MAX  =  127;
pub const U64_MAX = 18446744073709551615u;
pub const U32_MAX = 4294967295u;
pub const U16_MAX = 65535u;
pub const U8_MAX  = 255u;
pub const F64_MAX = 1.7976931348623157e+308;
pub const F64_MIN = 2.2250738585072014e-308;
pub const F32_MAX = 3.40282347e+38;
pub const F32_MIN = 1.17549435e-38;
```

### 3. `core::char_util`, Byte and character classification

All `u8`-taking predicates operate on a single byte; the `char*` variants operate
on a Coral `char` (Unicode scalar value).

```coral
// byte predicates / transforms (u8)
pub bool isDigit(u8 c)
pub bool isAlpha(u8 c)
pub bool isAlnum(u8 c)
pub bool isLower(u8 c)
pub bool isUpper(u8 c)
pub u8   toLower(u8 c)
pub u8   toUpper(u8 c)
pub bool isSpace(u8 c)
pub bool isPrint(u8 c)
pub bool isControl(u8 c)
pub bool isHexDigit(u8 c)
pub u8   digitValue(u8 c)
pub bool isAscii(u8 c)
pub bool isWhitespace(u8 c)   // alias of isSpace
pub bool isNewline(u8 c)
pub bool isPunctuation(u8 c)
pub bool isSymbol(u8 c)

// UTF-8 helpers
pub u32  utf8Width(u32 c)
pub u32  encodeUtf8(u32 c, u8* buf)
pub struct(u32, u32) decodeUtf8(const u8* buf)   // returns (codepoint, length)
pub u32  toUtf8(u32 c, u8* buf)
pub u32  fromUtf8(const u8* buf)
pub u32  toStr(u8 c, u8* buf)

// byte comparisons
pub u8   toAscii(u8 c)
pub bool u8Eq(u8 a, u8 b)
pub bool u8EqLower(u8 a, u8 b)
pub i32  u8Cmp(u8 a, u8 b)

// char (Unicode) variants
pub bool charIsValid(char c)
pub bool charIsAscii(char c)
pub bool charIsDigit(char c)
pub bool charIsAlpha(char c)
pub bool charIsAlnum(char c)
pub bool charIsUpper(char c)
pub bool charIsLower(char c)
pub bool charIsSpace(char c)
pub bool charIsControl(char c)
pub bool charIsPrint(char c)
pub char charToUpper(char c)
pub char charToLower(char c)
pub u32  charToU32(char c)
pub char charFromU32(u32 v)
pub bool charTryFromU32(u32 v, char* out)
pub u32  charEncodeUtf8(char c, u8* buf)
pub char charDecodeUtf8(const u8* buf, usize len, usize* consumed)

// constants
pub u8 const newline        = '\n';
pub u8 const tab            = '\t';
pub u8 const space          = ' ';
pub u8 const nullu8         = '\0';
pub u8 const carriageReturn = '\r';
```

### 4. `core::str`, Methods on the builtin `str`

`str` is a builtin view type:
```coral
struct str { const u8* ptr; usize len; }
```
Extended (imports `platform::libc` and `std::text::string`):

```coral
pub extend str
{
    static str fromCstr(const cchar::cchar* cstr)
    static str fromParts(const u8* ptr, usize len)
    static str empty()

    String       asString()
    const u8*    asU8()
    u8           at(usize idx)
    bool         isEmpty()
    bool         equals(str other)
    i32          compare(str other)
    bool         startsWith(str prefix)
    bool         endsWith(str suffix)
    bool         containsView(str needle)
    bool         containsByte(u8 c)
    usize        findByte(u8 c)
    usize        rfindByte(u8 c)
    usize        findView(str needle)
    str          slice(usize start, usize end)
    str          trimStart()
    str          trimEnd()
    str          trim()
    bool         isAsciiDigit()
    bool         isAsciiAlpha()
    bool         isAsciiAlnum()
    bool         nextCodepoint(usize* idx, char* out)
    usize        codepointCount()
}
```

---

## platform

### 5. `platform::libc`, Libc / pthread / POSIX externs
All declarations are `pub extern`. Grouped by area.

```coral
// stdio / errno
i32*  __errno_location()
i64   read(i32 fd, cchar* buf, u64 count)
i64   write(i32 fd, const cchar* buf, u64 count)
i32   getcchar()
i32   putcchar(i32 c)
i32   fflush(rawptr stream)
i32   getchar()
i32   printf(const cchar* fmt, ...)
i32   snprintf(cchar* buf, u64 size, const cchar* fmt, ...)
i32   vsnprintf(cchar* buf, u64 size, const cchar* fmt, ...)
i32   puts(const cchar* s)

// string / memory
u64   strlen(const cchar* s)
i32   strcmp(const cchar* a, const cchar* b)
cchar* strcpy(cchar* dst, const cchar* src)
i32   memcmp(const rawptr a, const rawptr b, u64 n)
rawptr malloc(u64 size)
void   free(rawptr ptr)
rawptr realloc(rawptr ptr, u64 newSize)

// files / dirs / fs
rawptr mmap(rawptr addr, u64 length, i32 prot, i32 flags, i32 fd, i64 offset)
i32   open(const cchar* path, i32 flags, i32 mode)
i32   close(i32 fd)
i32   stat(const cchar* path, rawptr buf)
i32   mkdir(const cchar* path, i32 mode)
i32   chdir(const cchar* path)
i32   rmdir(const cchar* path)
i32   unlink(const cchar* path)
i32   rename(const cchar* old, const cchar* newName)
i32   access(const cchar* path, i32 mode)
rawptr opendir(const cchar* path)
rawptr readdir(rawptr dir)
i32   closedir(rawptr dir)
i64   lseek(i32 fd, i64 offset, i32 whence)
i32   mkstemp(cchar* templateStr)
cchar* mkdtemp(cchar* templateStr)
f64   strtod(const cchar* nptr, cchar** endptr)
i64   readlink(const cchar* path, cchar* buf, u64 bufsize)
rawptr fopen(const cchar* path, const cchar* mode)
i32   fclose(rawptr stream)
u64   fread(rawptr ptr, u64 size, u64 count, rawptr stream)
u64   fwrite(const rawptr ptr, u64 size, u64 count, rawptr stream)
i32   feof(rawptr stream)
i32   ferror(rawptr stream)

// regex
i32   regcomp(rawptr preg, const cchar* pattern, i32 cflags)
i32   regexec(const rawptr preg, const cchar* string, u64 nmatch, rawptr pmatch, i32 eflags)
void  regfree(rawptr preg)
u64   regerror(i32 errcode, const rawptr preg, cchar* errbuf, u64 errbufSize)

// process / signals / time
i32   fork()
i32   execvp(const cchar* file, const cchar** argv)
i32   execvpe(const cchar* file, const cchar** argv, const cchar** envp)
i32   waitpid(i32 pid, i32* status, i32 options)
i32   poll(rawptr fds, u64 nfds, i32 timeout)
void  _exit(i32 code)
i32   pipe(i32* fds)
i32   dup2(i32 oldfd, i32 newfd)
i32   system(const cchar* cmd)
rawptr signal(i32 signum, rawptr handler)
i32   kill(i32 pid, i32 sig)
i32   raise(i32 sig)
i32   sched_yield()
i32   gettimeofday(rawptr tv, rawptr tz)
u64   time(rawptr t)
i64   clock_gettime(i32 clockId, rawptr tp)
i32   nanosleep(const rawptr req, rawptr rem)

// environment / tty
cchar* getenv(const cchar* name)
i32   setenv(const cchar* name, const cchar* value, i32 overwrite)
i32   unsetenv(const cchar* name)
cchar** environ;
i32   isatty(i32 fd)

// ucontext (used by std::concurrent::async)
i32   getcontext(rawptr uc)
void  makecontext(rawptr uc, void() fn, i32 argc)
i32   swapcontext(rawptr ocp, rawptr ucp)

// pthreads
i32   pthread_create(rawptr* thread, const rawptr attr, rawptr(rawptr) start, rawptr arg)
i32   pthread_join(rawptr thread, rawptr* retval)
void  pthread_exit(rawptr retval)
rawptr pthread_self()
i32   pthread_mutex_init(rawptr mutex, const rawptr attr)
i32   pthread_mutex_destroy(rawptr mutex)
i32   pthread_mutex_lock(rawptr mutex)
i32   pthread_mutex_unlock(rawptr mutex)
i32   pthread_mutex_trylock(rawptr mutex)
i32   pthread_mutexattr_init(rawptr attr)
i32   pthread_mutexattr_destroy(rawptr attr)
i32   pthread_mutexattr_settype(rawptr attr, i32 type)
i32   pthread_cond_init(rawptr cond, const rawptr attr)
i32   pthread_cond_destroy(rawptr cond)
i32   pthread_cond_wait(rawptr cond, rawptr mutex)
i32   pthread_cond_signal(rawptr cond)
i32   pthread_cond_broadcast(rawptr cond)
i32   pthread_cond_timedwait(rawptr cond, rawptr mutex, rawptr abstime)
i32   pthread_rwlock_init(rawptr lock, const rawptr attr)
i32   pthread_rwlock_destroy(rawptr lock)
i32   pthread_rwlock_rdlock(rawptr lock)
i32   pthread_rwlock_wrlock(rawptr lock)
i32   pthread_rwlock_unlock(rawptr lock)
i32   pthread_rwlock_tryrdlock(rawptr lock)
i32   pthread_rwlock_trywrlock(rawptr lock)
i32   sem_init(rawptr sem, i32 pshared, u32 value)
i32   sem_destroy(rawptr sem)
i32   sem_wait(rawptr sem)
i32   sem_trywait(rawptr sem)
i32   sem_post(rawptr sem)
i32   sem_getvalue(rawptr sem, i32* sval)

// sockets
i32   socket(i32 domain, i32 type, i32 protocol)
i32   connect(i32 fd, const rawptr addr, i32 addrlen)
i32   bind(i32 fd, const rawptr addr, i32 addrlen)
i32   listen(i32 fd, i32 backlog)
i32   accept(i32 fd, rawptr addr, i32* addrlen)
i32   setsockopt(i32 fd, i32 level, i32 optname, const u8* optval, i32 optlen)
i64   send(i32 fd, const u8* buf, u64 len, i32 flags)
i64   recv(i32 fd, u8* buf, u64 len, i32 flags)
i64   sendto(i32 fd, const u8* buf, u64 len, i32 flags, const rawptr dstAddr, i32 addrLen)
i64   recvfrom(i32 fd, u8* buf, u64 len, i32 flags, rawptr srcAddr, i32* addrLen)
u32   htonl(u32 hostlong)
u16   htons(u16 hostshort)
```

### 6. `platform::win32`, Win32 / Winsock / CRT externs
All `pub extern`. This is the Windows counterpart of `platform::libc`.

```coral
// console / handles / files
rawptr GetStdHandle(u32 nStdHandle)
bool   ReadFile(rawptr hFile, cchar* lpBuffer, u32 nNumberOfBytesToRead, u32* lpNumberOfBytesRead, rawptr lpOverlapped)
bool   WriteFile(rawptr hFile, const cchar* lpBuffer, u32 nNumberOfBytesToWrite, u32* lpNumberOfBytesWritten, rawptr lpOverlapped)
void   ExitProcess(u32 uExitCode)
rawptr CreateFileA(const cchar* lpFileName, u32 dwDesiredAccess, u32 dwShareMode, rawptr lpSecurityAttributes, u32 dwCreationDisposition, u32 dwFlagsAndAttributes, rawptr hTemplateFile)
bool   CloseHandle(rawptr hObject)
bool   DeleteFileA(const cchar* lpFileName)
bool   RemoveDirectoryA(const cchar* lpPathName)
bool   CreateDirectoryA(const cchar* lpPathName, rawptr lpSecurityAttributes)
bool   MoveFileA(const cchar* lpExistingFileName, const cchar* lpNewFileName)
u32    GetFileAttributesA(const cchar* lpFileName)

// virtual memory / mapping / heap
rawptr VirtualAlloc(rawptr lpAddress, u64 dwSize, u32 flAllocationType, u32 flProtect)
bool   VirtualFree(rawptr lpAddress, u64 dwSize, u32 dwFreeType)
rawptr CreateFileMappingA(rawptr hFile, rawptr lpAttributes, u32 flProtect, u32 dwMaximumSizeHigh, u32 dwMaximumSizeLow, const cchar* lpName)
rawptr MapViewOfFile(rawptr hFileMappingObject, u32 dwDesiredAccess, u32 dwFileOffsetHigh, u32 dwFileOffsetLow, u64 dwNumberOfBytesToMap)
bool   UnmapViewOfFile(rawptr lpBaseAddress)
rawptr GetProcessHeap()
rawptr HeapAlloc(rawptr hHeap, u32 dwFlags, u64 dwBytes)
bool   HeapFree(rawptr hHeap, u32 dwFlags, rawptr lpMem)
rawptr HeapReAlloc(rawptr hHeap, u32 dwFlags, rawptr lpMem, u64 dwBytes)

// threads / sync primitives
rawptr CreateThread(rawptr lpThreadAttributes, u64 dwStackSize, u32(rawptr) lpStartAddress, rawptr lpParameter, u32 dwCreationFlags, u32* lpThreadId)
u32    WaitForSingleObject(rawptr hHandle, u32 dwMilliseconds)
bool   TerminateThread(rawptr hThread, u32 dwExitCode)
bool   GetExitCodeThread(rawptr hThread, u32* lpExitCode)
rawptr CreateMutexA(rawptr lpMutexAttributes, bool bInitialOwner, const cchar* lpName)
bool   ReleaseMutex(rawptr hMutex)
rawptr CreateSemaphoreA(rawptr lpSemaphoreAttributes, i32 lInitialCount, i32 lMaximumCount, const cchar* lpName)
bool   ReleaseSemaphore(rawptr hSemaphore, i32 lReleaseCount, i32* lpPreviousCount)
rawptr CreateEventA(rawptr lpEventAttributes, bool bManualReset, bool bInitialState, const cchar* lpName)
bool   SetEvent(rawptr hEvent)
bool   ResetEvent(rawptr hEvent)
void   InitCriticalSection(rawptr lpCriticalSection)
void   DeleteCriticalSection(rawptr lpCriticalSection)
void   EnterCriticalSection(rawptr lpCriticalSection)
void   LeaveCriticalSection(rawptr lpCriticalSection)
bool   TryEnterCriticalSection(rawptr lpCriticalSection)
void   InitializeSRWLock(rawptr srwlock)
void   AcquireSRWLockExclusive(rawptr srwlock)
void   ReleaseSRWLockExclusive(rawptr srwlock)
void   AcquireSRWLockShared(rawptr srwlock)
void   ReleaseSRWLockShared(rawptr srwlock)
bool   TryAcquireSRWLockExclusive(rawptr srwlock)
bool   TryAcquireSRWLockShared(rawptr srwlock)
void   InitializeConditionVariable(rawptr cond)
bool   SleepConditionVariableCS(rawptr cond, rawptr critsec, u32 dwMilliseconds)
void   WakeConditionVariable(rawptr cond)
void   WakeAllConditionVariable(rawptr cond)

// processes / fibers
rawptr OpenProcess(u32 dwDesiredAccess, bool bInheritHandle, u32 dwProcessId)
bool   TerminateProcess(rawptr hProcess, u32 uExitCode)
bool   GetExitCodeProcess(rawptr hProcess, u32* lpExitCode)
rawptr GetCurrentProcess()
u32    GetCurrentProcessId()
u32    GetCurrentThreadId()
void   ExitThread(u32 dwExitCode)
u32    ResumeThread(rawptr hThread)
u32    SuspendThread(rawptr hThread)
bool   DuplicateHandle(rawptr hSourceProcessHandle, rawptr hSourceHandle, rawptr hTargetProcessHandle, rawptr* lpTargetHandle, u32 dwDesiredAccess, bool bInheritHandle, u32 dwOptions)
u32    WaitForMultipleObjects(u32 nCount, const rawptr* lpHandles, bool bWaitAll, u32 dwMilliseconds)
bool   SwitchToThread()
bool   SetThreadPriority(rawptr hThread, i32 nPriority)
i32    GetThreadPriority(rawptr hThread)
rawptr CreateFiber(u64 dwStackSize, u32(rawptr) lpStartAddress, rawptr lpParameter)
void   SwitchToFiber(rawptr lpFiber)
void   DeleteFiber(rawptr lpFiber)
rawptr ConvertThreadToFiber(rawptr lpParameter)
bool   CreatePipe(rawptr* hReadPipe, rawptr* hWritePipe, rawptr lpPipeAttributes, u32 nSize)
bool   CreateProcessA(const cchar* lpApplicationName, cchar* lpCommandLine, rawptr lpProcessAttributes, rawptr lpThreadAttributes, bool bInheritHandles, u32 dwCreationFlags, rawptr lpEnvironment, const cchar* lpCurrentDirectory, rawptr lpStartupInfo, rawptr lpProcessInformation)
bool   SetHandleInformation(rawptr hObject, u32 dwMask, u32 dwFlags)
bool   PeekNamedPipe(rawptr hNamedPipe, rawptr lpBuffer, u32 nBufferSize, u32* lpBytesRead, u32* lpTotalBytesAvail, u32* lpBytesLeftThisMessage)

// file positioning / enumeration
u32    SetFilePointerA(rawptr hFile, i32 lDistanceToMove, i32* lpDistanceToMoveHigh, u32 dwMoveMethod)
bool   GetFileAttributesExA(const cchar* lpFileName, u32 fInfoLevelId, rawptr lpFileInformation)
rawptr FindFirstFileA(const cchar* lpFileName, rawptr lpFindFileData)
bool   FindNextFileA(rawptr hFindFile, rawptr lpFindFileData)
bool   FindClose(rawptr hFindFile)
u32    GetFileSize(rawptr hFile, u32* lpFileSizeHigh)
bool   GetFileSizeEx(rawptr hFile, i64* lpFileSize)
bool   FlushFileBuffers(rawptr hFile)
u32    GetFileType(rawptr hFile)
bool   GetFileInformationByHandle(rawptr hFile, rawptr lpFileInformation)
u32    GetFullPathNameA(const cchar* lpFileName, u32 nBufferLength, cchar* lpBuffer, cchar** lpFilePart)
u32    GetCurrentDirectoryA(u32 nBufferLength, cchar* lpBuffer)
bool   SetCurrentDirectoryA(const cchar* lpPathName)
bool   CopyFileA(const cchar* lpExistingFileName, const cchar* lpNewFileName, bool bFailIfExists)
bool   LockFile(rawptr hFile, u32 dwReserved, u32 nNumberOfBytesToLockLow, u32 nNumberOfBytesToLockHigh)
bool   UnlockFile(rawptr hFile, u32 dwReserved, u32 nNumberOfBytesToUnlockLow, u32 nNumberOfBytesToUnlockHigh)
u32    GetTempPathA(u32 nBufferLength, cchar* lpBuffer)
u32    GetTempFileNameA(const cchar* lpPathName, const cchar* lpPrefixString, u32 uUnique, cchar* lpTempFileName)

// errors / debug
u32    GetLastError()
void   SetLastError(u32 dwErrCode)
u32    FormatMessageA(u32 dwFlags, rawptr lpSource, u32 dwMessageId, u32 dwLanguageId, cchar* lpBuffer, u32 nSize, rawptr Arguments)
void   OutputDebugStringA(const cchar* lpOutputString)
bool   IsDebuggerPresent()

// console
bool   ReadConsoleA(rawptr hConsoleInput, rawptr lpBuffer, u32 nNumberOfCharsToRead, u32* lpNumberOfCharsRead, rawptr pReserved)
bool   WriteConsoleA(rawptr hConsoleOutput, const cchar* lpBuffer, u32 nNumberOfCharsToWrite, u32* lpNumberOfCharsWritten, rawptr lpReserved)
bool   SetConsoleTextAttribute(rawptr hConsoleOutput, u16 wAttributes)
bool   GetConsoleScreenBufferInfo(rawptr hConsoleOutput, rawptr lpConsoleScreenBufferInfo)
bool   SetConsoleTitleA(const cchar* lpConsoleTitle)
u32    GetConsoleTitleA(cchar* lpConsoleTitle, u32 nSize)
bool   AllocConsole()

// memory protection / globals / modules
bool   VirtualProtect(rawptr lpAddress, u64 dwSize, u32 flNewProtect, u32* lpflOldProtect)
u64    VirtualQuery(rawptr lpAddress, rawptr lpBuffer, u64 dwLength)
rawptr GlobalAlloc(u32 uFlags, u64 dwBytes)
rawptr GlobalFree(rawptr hMem)
rawptr GlobalLock(rawptr hMem)
bool   GlobalUnlock(rawptr hMem)
rawptr LoadLibraryA(const cchar* lpLibFileName)
bool   FreeLibrary(rawptr hLibModule)
rawptr GetProcAddress(rawptr hModule, const cchar* lpProcName)
rawptr GetModuleHandleA(const cchar* lpModuleName)
u32    GetModuleFileNameA(rawptr hModule, cchar* lpFilename, u32 nSize)

// time / environment
bool   QueryPerformanceCounter(i64* lpPerformanceCount)
bool   QueryPerformanceFrequency(i64* lpFrequency)
void   GetLocalTime(rawptr lpSystemTime)
void   GetSystemTime(rawptr lpSystemTime)
void   GetSystemTimeAsFileTime(rawptr lpSystemTimeAsFileTime)
u32    GetTickCount()
u64    GetTickCount64()
void   Sleep(u32 dwMilliseconds)
bool   FileTimeToSystemTime(const rawptr lpFileTime, rawptr lpSystemTime)
bool   SystemTimeToFileTime(const rawptr lpSystemTime, rawptr lpFileTime)
cchar* GetEnvironmentVariableA(const cchar* lpName, cchar* lpBuffer, u32 nSize)
bool   SetEnvironmentVariableA(const cchar* lpName, const cchar* lpValue)
cchar* GetEnvironmentStringsA()
bool   FreeEnvironmentStringsA(cchar* lpEnvBlock)
cchar* GetCommandLineA()
bool   GetConsoleMode(rawptr hConsoleHandle, u32* lpMode)
bool   SetConsoleMode(rawptr hConsoleHandle, u32 dwMode)

// Winsock
i32    WSAStartup(u16 wVersionRequired, rawptr lpWSAData)
i32    WSACleanup()
rawptr socket(i32 af, i32 type, i32 protocol)
i32    bind(rawptr s, const rawptr name, i32 namelen)
i32    listen(rawptr s, i32 backlog)
rawptr accept(rawptr s, rawptr addr, i32* addrlen)
i32    connect(rawptr s, const rawptr name, i32 namelen)
i32    send(rawptr s, const cchar* buf, i32 len, i32 flags)
i32    recv(rawptr s, cchar* buf, i32 len, i32 flags)
i32    closesocket(rawptr s)
i32    setsockopt(rawptr s, i32 level, i32 optname, const cchar* optval, i32 optlen)
i32    getsockopt(rawptr s, i32 level, i32 optname, cchar* optval, i32* optlen)
i64    recvfrom(rawptr s, cchar* buf, u64 len, i32 flags, rawptr srcAddr, i32* addrLen)
i64    sendto(rawptr s, const cchar* buf, u64 len, i32 flags, const rawptr dstAddr, i32 addrLen)
u32    htonl(u32 val)
u16    htons(u16 hostshort)
u32    ntohl(u32 val)
u16    ntohs(u16 val)
i32    shutdown(rawptr s, i32 how)
i32    ioctlsocket(rawptr s, i32 cmd, u32* argp)
i32    WSAGetLastError()
void   WSASetLastError(i32 iError)
u32    inet_addr(const cchar* cp)
i32    BCryptGenRandom(rawptr pbBuffer, u32 cbBuffer, u32 dwFlags)

// libm
f64    sin(f64 x)  cos(f64 x)  tan(f64 x)  sqrt(f64 x)  pow(f64 x, f64 y)
f64    floor(f64 x) ceil(f64 x) fabs(f64 x) asin(f64 x) acos(f64 x) atan(f64 x)
f64    atan2(f64 y, f64 x) sinh(f64 x) cosh(f64 x) tanh(f64 x) cbrt(f64 x)
f64    exp(f64 x) log(f64 x) log2(f64 x) log10(f64 x) round(f64 x)
f64    fmod(f64 x, f64 y) hypot(f64 x, f64 y) erf(f64 x) erfc(f64 x)
f64    tgamma(f64 x) lgamma(f64 x)
```

---

## std::collections

Imported via `std::collections`. `Vec<T>` is also re-exported as `std::vec` and
prelude-imported; `Arr<T, N>` as `std::arr`.

### 7. `std::collections::arr`, `Arr<T, N>`

```coral
pub struct Arr<T, N>
{
    T data[N];

    #[[inline]] T*       ptr()
    #[[inline]] const T* constPtr()
    #[[inline]] usize    count()          // == N
    bool        isEmpty()
    T           at(usize i)
    void        set(usize i, T val)
    T*          atPtr(usize i)
    T           front()
    T           back()
    void        fill(T val)
    void        copyTo(T* dst)
    void        copyFrom(const T* src)
}
```

### 8. `std::collections::vec`, `Vec<T>` (aka `std::vec`)

```coral
pub struct Vec<T>
{
    T* data;
    usize len;
    usize cap;

    static Vec<T> new()
    static Vec<T> withCap(usize capacity)
    void   reserve(usize newCap)
    void   reserveExact(usize newCap)
    void   push(T val)
    T      pop()
    usize  count()
    T*     atPtr(usize i)
    const T* atConst(usize i)
    T      at(usize i)
    T*     ptr()
    bool   isEmpty()
    const T* constPtr()
    void   set(usize i, T val)
    T      front()
    T      back()
    void   insert(usize i, T val)
    void   removeAt(usize i)
    void   removeRange(usize start, usize end)
    bool   contains(T val)
    void   fill(T val)
    void   shrinkToFit()
    void   clear()
    void   reverse()
    bool   isSortedBy(bool(T, T) less)
    void   sortBy(bool(T, T) less)
    i64    binarySearchBy(T key, i32(T, T) cmp)
    void   dispose()
}
// helper: void _sortByRange(usize lo, usize hi, bool(T, T) less)
//         usize _partitionBy(usize lo, usize hi, bool(T, T) less)
pub extend<T> Vec<T> : @drop { void drop(); }
```

### 9. `std::collections::bitset`, `Bitset`

```coral
pub struct Bitset
{
    u64* words;
    u64  numBits;
    u64  numWords;

    static Bitset new(u64 numBits)
    void dispose()
    u64  count()          // numBits
    u64  wordCount()
    void set(u64 bit)
    void clear(u64 bit)
    void toggle(u64 bit)
    bool test(u64 bit)
    void setAll()
    void clearAll()
    u64  countOnes()
    u64  countZeros()
    bool hasAny()
    bool none()
    bool all()
    void and(Bitset* other)
    void or(Bitset* other)
    void xor(Bitset* other)
    void not()
    void _maskPadding()
}
pub extend Bitset : @drop { void drop(); }
```

### 10. `std::collections::cache`, LRU `Cache<K, V>`

```coral
pub struct CacheEntry<K, V>
{
    K key;
    V value;
    CacheEntry<K, V>* prev;
    CacheEntry<K, V>* next;
}

pub struct Cache<K, V>
{
    HashMap<K, CacheEntry<K, V>*> map;
    CacheEntry<K, V>* head;
    CacheEntry<K, V>* tail;
    usize maxSize;
    usize(K) hashFn;
    bool(K, K) eqFn;

    static Cache<K, V> new(usize max, usize(K) hf, bool(K, K) ef)
    void   dispose()
    usize  count()
    usize  maxSizeValue()
    Result<V, CollectionError> insert(K key, V value)
    Option<V>  get(K key)
    Option<V*> getPtr(K key)
    bool   contains(K key)
    void   remove(K key)
    void   clear()
    void   each(void(K, V) fn)
    void   resize(usize newMax)
    // helper: void _moveToFront(CacheEntry<K, V>* entry); void _evict();
}
pub extend<K, V> Cache<K, V> : @drop { void drop(); }
```

### 11. `std::collections::deque`, `Deque<T>`

```coral
pub struct Deque<T>
{
    T* data;
    usize head;
    usize tail;
    usize cap;
    usize mask;

    static Deque<T> new()
    void   dispose()
    usize  count()
    bool   isEmpty()
    usize  capacity()
    void   pushFront(T val)
    void   pushBack(T val)
    T      popFront()
    T      popBack()
    T      front()
    T      back()
    T      at(usize i)
    void   set(usize i, T val)
    void   clear()
    void   _grow()
}
pub extend<T> Deque<T> : @drop { void drop(); }
```

### 12. `std::collections::hashmap`, `HashMap<K, V>`

```coral
pub variant CollectionError { AllocFailed { str msg; } }

pub struct HashMapEntry<K, V>
{
    K key;
    V value;
    bool occupied;
}

pub struct HashMap<K, V>
{
    HashMapEntry<K, V>* entries;
    usize cap;
    usize len;
    usize(K) hashFn;
    bool(K, K) eqFn;

    static HashMap<K, V> new(usize(K) hf, bool(K, K) ef)
    void   dispose()
    usize  count()
    Result<V, CollectionError> insert(K key, V value)
    Option<V>   get(K key)
    bool        contains(K key)
    Option<V*>  getPtr(K key)
    void        remove(K key)
    Option<HashMapEntry<K, V>> removeEntry(K key)   // backward-shift deletion
    void        clear()
    Vec<K>      keys()
    Vec<V>      values()
    void        each(void(K, V) fn)
    void        eachEntry(void(HashMapEntry<K, V>*) fn)
}
pub extend<K, V> HashMap<K, V> : @drop { void drop(); }
```

### 13. `std::collections::iter`, Generic iteration helpers
Free functions over `Vec<T>`.

```coral
pub Vec<U> map<T, U>(const Vec<T>* v, U(T) fn)
pub Vec<T> filter<T>(const Vec<T>* v, bool(T) pred)
pub T      reduce<T>(const Vec<T>* v, T init, T(T, T) fn)
pub void   forEach<T>(const Vec<T>* v, void(T) fn)
pub T      find<T>(const Vec<T>* v, bool(T) pred)
pub isize  findIndex<T>(const Vec<T>* v, bool(T) pred)
pub bool   hasAny<T>(const Vec<T>* v, bool(T) pred)
pub bool   all<T>(const Vec<T>* v, bool(T) pred)
pub Vec<T> take<T>(const Vec<T>* v, usize n)
pub Vec<T> skip<T>(const Vec<T>* v, usize n)
pub Vec<T> slice<T>(const Vec<T>* v, usize start, usize end)
pub usize  countIf<T>(const Vec<T>* v, bool(T) pred)
pub T      minBy<T>(const Vec<T>* v, bool(T, T) less)
pub T      maxBy<T>(const Vec<T>* v, bool(T, T) less)
pub Vec<T> unique<T>(const Vec<T>* v, bool(T, T) eq)
pub Vec<T> flatten<T>(const Vec<Vec<T>>* v)
pub Vec<usize> enumerate<T>(const Vec<T>* v)
pub T      sum<T>(const Vec<T>* v)
pub f64    average(const Vec<f64>* v)

pub struct Pair<T, U> { T first; U second; }
pub Vec<Pair<T, U>> zip<T, U>(const Vec<T>* a, const Vec<U>* b)
```

### 14. `std::collections::linkedlist`, `LinkedList<T>`

```coral
pub struct ListNode<T>
{
    T value;
    ListNode<T>* prev;
    ListNode<T>* next;
}

pub struct LinkedList<T>
{
    ListNode<T>* head;
    ListNode<T>* tail;
    usize len;

    static LinkedList<T> new()
    void dispose()
    usize count()
    bool  isEmpty()
    void  pushFront(T val)
    void  pushBack(T val)
    T     popFront()
    T     popBack()
    T     front()
    T     back()
    void  insertAfter(ListNode<T>* node, T val)
    void  remove(ListNode<T>* node)
    void  each(void(T) fn)
}
pub extend<T> LinkedList<T> : @drop { void drop(); }
```

### 15. `std::collections::map`, Ordered AVL `Map<K, V>`

```coral
pub variant CollectionError { AllocFailed { str msg; } }

pub struct MapEntry<K, V>
{
    K key;
    V value;
    i32 height;
    MapEntry<K, V>* left;
    MapEntry<K, V>* right;
}

pub struct Map<K, V>
{
    MapEntry<K, V>* root;
    usize len;
    i32(K, K) cmpFn;
    bool failed;

    static Map<K, V> new(i32(K, K) cmp)
    void dispose()
    usize count()
    bool  isEmpty()
    Result<V, CollectionError> insert(K key, V value)
    Option<V>  get(K key)
    Option<V*> getPtr(K key)
    bool  contains(K key)
    void  remove(K key)
    void  clear()
    void  each(void(K, V) fn)
    // helpers: _max _height _balance _rotateRight _rotateLeft _insert
    //          _findMin _remove _find _eachInOrder _disposeNode
}
pub extend<K, V> Map<K, V> : @drop { void drop(); }
```

### 16. `std::collections::priorityqueue`, `PriorityQueue<T>`

```coral
pub struct PriorityQueue<T>
{
    T* data;
    usize len;
    usize cap;
    bool(T, T) less;      // constructor takes `cmp`

    static PriorityQueue<T> new(bool(T, T) cmp)
    void dispose()
    usize count()
    bool  isEmpty()
    void  push(T val)
    T     pop()
    T     peek()
    void  clear()
    // helpers: _grow _siftUp _siftDown
}
pub extend<T> PriorityQueue<T> : @drop { void drop(); }
```

### 17. `std::collections::queue`, FIFO `Queue<T>`

Wraps `Deque<T>`.

```coral
pub struct Queue<T>
{
    deque::Deque<T> inner;

    static Queue<T> new()
    void dispose()
    usize count()
    bool  isEmpty()
    void  enqueue(T val)
    T     dequeue()
    T     peek()
    void  clear()
}
pub extend<T> Queue<T> : @drop { void drop(); }
```

### 18. `std::collections::ringbuf`, `RingBuf<T>`

```coral
pub struct RingBuf<T>
{
    T* data;
    usize cap;
    usize head;
    usize tail;
    bool full;

    static RingBuf<T> new(usize capacity)
    void dispose()
    usize count()
    bool  isEmpty()
    bool  isFull()
    usize capacity()
    void  push(T val)
    T     pop()
    T     front()
    T     back()
    T     at(usize i)
    void  clear()
}
pub extend<T> RingBuf<T> : @drop { void drop(); }
```

### 19. `std::collections::set`, `Set<T>`

```coral
pub struct Set<T>
{
    HashMap<T, bool> inner;
    usize(T) hashFn;
    bool(T, T) eqFn;

    static Set<T> new(usize(T) hf, bool(T, T) ef)
    void dispose()
    usize count()
    bool  isEmpty()
    void  insert(T val)
    bool  contains(T val)
    void  remove(T val)
    void  clear()
    Vec<T> toVec()
    void  each(void(T) fn)
    Set<T> union(const Set<T>* other)
    Set<T> intersection(const Set<T>* other)
    Set<T> difference(const Set<T>* other)
    bool  isSubset(const Set<T>* other)
    bool  isSuperset(const Set<T>* other)
}
pub extend<T> Set<T> : @drop { void drop(); }
```

### 20. `std::collections::sort`, Sorting and searching
Free functions; `*Range`/`partition*` variants are internal helpers.

```coral
pub void  sortI32(Vec<i32>* v)
pub void  sortusize(Vec<usize>* v)
pub void  sortF64(Vec<f64>* v)
pub void  sortBy<T>(Vec<T>* v, bool(T, T) less)
pub bool  isSortedI32(const Vec<i32>* v)
pub bool  isSortedusize(const Vec<usize>* v)
pub bool  isSortedBy<T>(const Vec<T>* v, bool(T, T) less)
pub isize binarySearchI32(const Vec<i32>* v, i32 key)
pub isize binarySearchusize(const Vec<usize>* v, usize key)
pub isize binarySearchBy<T>(const Vec<T>* v, T key, i32(T, T) cmp)
pub void  reverse<T>(Vec<T>* v)
```

### 21. `std::collections::tree`, `Tree<T>` (n-ary)

```coral
pub struct TreeNode<T>
{
    T value;
    Vec<TreeNode<T>*> children;
}

pub struct Tree<T>
{
    TreeNode<T>* root;

    static Tree<T> new()
    void dispose()
    bool isEmpty()
    TreeNode<T>* setRoot(T val)
    TreeNode<T>* addChild(TreeNode<T>* parent, T val)
    usize childCount(TreeNode<T>* node)
    Option<TreeNode<T>*> childAt(TreeNode<T>* node, usize idx)
    void removeChild(TreeNode<T>* parent, usize idx)
    void preOrder(void(T) fn)
    void postOrder(void(T) fn)
    usize depth(TreeNode<T>* node)
    usize size()
    Vec<T> toVec()
    // helpers: _disposeNode _preOrder _postOrder _count _toVec
}
pub extend<T> Tree<T> : @drop { void drop(); }
```

### 22. `std::collections::trie`, `Trie` (byte-keyed)

```coral
const u32 TRIE_FANOUT = 256;

pub struct TrieNode
{
    TrieNode* children[TRIE_FANOUT];
    bool isEnd;
}

pub struct Trie
{
    TrieNode* root;
    usize count;

    static Trie new()
    void dispose()
    usize size()
    bool  isEmpty()
    void  insert(str key)
    bool  contains(str key)
    bool  startsWith(str prefix)
    bool  remove(str key)
    void  each(void(str) fn)
    // helpers: _disposeNode _remove _maxDepth _each
}
pub extend Trie : @drop { void drop(); }
```

### 23. `std::collections::unordered_map`, `UnorderedMap<K, V>`
Thin wrapper over `HashMap<K, V>`.

```coral
pub struct UnorderedMap<K, V>
{
    HashMap<K, V> inner;

    static UnorderedMap<K, V> new(usize(K) hf, bool(K, K) ef)
    void dispose()
    usize count()
    bool  isEmpty()
    Result<V, CollectionError> insert(K key, V value)
    Option<V>   get(K key)
    Option<V*>  getPtr(K key)
    bool        contains(K key)
    void        remove(K key)
    void        clear()
    Vec<K>      keys()
    Vec<V>      values()
    void        each(void(K, V) fn)
}
pub extend<K, V> UnorderedMap<K, V> : @drop { void drop(); }
```

---

## std::text

`String` is re-exported into the prelude.

### 24. `std::text::ascii`, ASCII / UTF-8 helpers

```coral
pub bool isAscii(u8 b)
pub bool isAsciiDigit(u8 b)
pub bool isAsciiAlpha(u8 b)
pub bool isAsciiAlnum(u8 b)
pub bool isAsciiHex(u8 b)
pub bool isAsciiSpace(u8 b)
pub bool isAsciiUpper(u8 b)
pub bool isAsciiLower(u8 b)
pub u8   toAsciiLower(u8 b)
pub u8   toAsciiUpper(u8 b)
pub u8   asciiDigitVal(u8 b)
pub u8   asciiHexVal(u8 b)

pub u32  utf8ByteCount(u8 b)
pub u32  utf8Decode(const u8* buf, u32* bytesOut)
pub u32  utf8Encode(u32 cp, u8* buf)
pub u32  utf16ToUtf8(u16 cp, u8* buf)
pub usize utf8CountChars(str s)
pub bool utf8IsValid(str s)
```

### 25. `std::text::string`, `String`

```coral
pub struct String
{
    u8* ptr;
    usize len;
    usize cap;

    static String new()
    static String withCap(usize cap)
    static String from(str sv)
    static String fromCstr(const cchar* cstr)
    static String join(str sep, const Vec<str>* parts)

    String clone()
    void   free()
    str    asView()
    cchar* asCstr()
    u8*    asU8()

    void   pushChar(u8 c)          // one raw byte
    void   pushCodepoint(char c)   // one UTF-8 codepoint
    void   pushByte(u8 b)
    void   appendView(str sv)
    void   pushView(str sv)
    void   pushStr(const String* other)
    void   pushCstr(const u8* cstr)
    void   pushRepeat(u8 c, usize n)

    void   clear()
    void   shrinkToFit()
    void   truncate(usize newLen)
    void   insertView(usize idx, str sv)
    void   removeRange(usize start, usize end)
    void   replaceAll(str needle, str replacement)
    void   toUpper()
    void   toLower()
    void   reverse()

    u8     at(usize idx)
    void   atApply(usize idx, u8 c)
    bool   isEmpty()
    bool   equals(const String* other)
    bool   equalsView(str sv)
    i32    compare(const String* other)
    usize  findChar(u8 c)
    usize  rfindChar(u8 c)
    usize  findView(str needle)
    bool   startsWith(str prefix)
    bool   endsWith(str suffix)
    bool   containsView(str needle)

    String trim()
    String trimStart()
    String trimEnd()
    String substr(usize start, usize end)
    Vec<str> splitByte(u8 delim)
    String repeat(usize n)
    String padLeft(usize totalLen, u8 padChar)
    String padRight(usize totalLen, u8 padChar)
    usize  countChar(u8 c)

    bool   nextCodepoint(usize* idx, char* out)
    usize  codepointCount()
    // helper: void _ensure(usize extra)
}
pub extend String : @drop { void drop(); }
```

### 26. `std::text::strutil`, String-view utilities

```coral
pub usize  split(str sv, u8 delim, str* out, usize maxParts)
pub Vec<str> splitVec(str sv, u8 delim)
pub str    trim(str sv)
pub str    trimLeft(str sv)
pub str    trimRight(str sv)
pub bool   startsWith(str sv, str prefix)
pub bool   endsWith(str sv, str suffix)
pub bool   contains(str sv, str sub)
pub isize  indexOf(str sv, str sub)
pub isize  indexOfChar(str sv, u8 ch)
pub isize  lastIndexOf(str sv, str sub)
pub String replace(str sv, str from, str to)
pub String join(const str* parts, usize count, str sep)
pub String joinVec(const Vec<str>* parts, str sep)
pub str    substr(str sv, usize start, usize len)
pub bool   equalsIgnoreCase(str a, str b)
```

### 27. `std::text::utf8`, UTF-8 codec

```coral
pub u8     encodeCodepoint(u32 cp, u8* out)
pub u32    decodeCodepoint(const u8* s, usize len, usize* consumed)
pub usize  codepointLen(const u8* s, usize len)
pub usize  countCodepoints(const u8* s, usize len)
pub bool   isValid(const u8* s, usize len)
pub String toLower(const u8* s, usize len)
pub String toUpper(const u8* s, usize len)
pub Option<char> nextChar(const u8* s, usize len, usize* consumed)
pub String encodeChar(char c)
```

### 28. `std::text::uri`, `Uri`

```coral
pub struct Uri
{
    String scheme;
    String userInfo;
    String host;
    u16    port;
    String path;
    String query;
    String fragment;
    bool   hasPort;

    static Uri new()
    void dispose()
    bool parse(str input)
}
pub extend Uri : @drop { void drop(); }
```

### 29. `std::text::regex`, `Regex` (POSIX ERE via libc)

```coral
const i32 REG_EXTENDED = 1;
const i32 REG_ICASE    = 2;
const i32 REG_NOSUB    = 4;

pub struct Regex
{
    rawptr impl[8];
    bool   compiled;
    usize  groupCount;
    u8*    findBuf;
    usize  findBufCap;

    bool compile(str pattern, bool caseInsensitive)
    void free()
    bool matches(str input)
    bool find(str input, Vec<str>* groups)
}
pub i32 regexFlags(bool extended, bool icase, bool nosub)
pub extend Regex : @drop { void drop(); }
```

---

## std::data

### 30. `std::data::option`, `Option<T>` (aka `std::option`, prelude)

```coral
pub variant Option<T>
{
    None,
    Some { T value; }
}

pub extend<T> Option<T>
{
    bool isSome()
    bool isNone()
    T    unwrap()
    T    unwrapOr(T default)
    T*   ptr()
    const T* constPtr()
    void map(T(T) fn)
    void andThen(Option<T>(T) fn)
    void orElse(Option<T>() fn)
    T    take()
}
```

### 31. `std::data::result`, `Result<T, E>` (aka `std::result`, prelude)

```coral
pub variant Result<T, E>
{
    Ok  { T value; },
    Err { E error; }
}

pub extend<T, E> Result<T, E>
{
    bool isOk()
    bool isErr()
    T    unwrap()
    T    unwrapOr(T defaultVal)
    E    unwrapErr()
    T*   okPtr(self)
    E*   errPtr(self)
    void mapOk(T(T) fn)
    void mapErr(E(E) fn)
    void andThen(Result<T, E>(T) fn)
    void orElse(Result<T, E>(E) fn)
}
```

---

## std::time

### 32. `std::time`, Wall-clock and monotonic time

Ported from the old `std/core/time` module. Each target implements the same
public surface with its own native clock: the Linux build issues raw x86_64
syscalls (`clock_gettime`, `gettimeofday`, `nanosleep`, `time`); the Windows
build calls `QueryPerformanceCounter`, `GetSystemTimeAsFileTime`, and `Sleep`.
There is no libc in either path.

```coral
pub const CLOCK_REALTIME  : i32 = 0;
pub const CLOCK_MONOTONIC : i32 = 1;

pub struct Timespec { i64 sec; i64 nsec; }
pub struct Timeval  { i64 sec; i64 usec; }

pub Timespec nowMonotonic()                       // CLOCK_MONOTONIC
pub Timespec nowRealtime()                        // CLOCK_REALTIME
pub Timeval  nowTimeval()                         // gettimeofday / derived
pub u64      unixSeconds()                        // time(2) / file-time epoch
pub Timespec addTimespec(Timespec a, Timespec b)
pub Timespec subTimespec(Timespec a, Timespec b)
pub f64      timespecToF64(Timespec ts)           // sec + nsec * 1e-9
pub f64      timevalToF64(Timeval tv)             // sec + usec * 1e-6
pub void     sleepTimespec(Timespec ts)           // nanosleep / Sleep
pub void     sleepMs(u64 ms)
```

- `nowMonotonic()` never jumps backwards and is the clock to use for measuring
  elapsed time; `nowRealtime()` is wall-clock and can move when the system time
  is adjusted.
- `sleepTimespec` / `sleepMs` do not retry a shortened sleep; a signal can wake
  them early (matching the old module).
- `Timespec` / `Timeval` are plain value types with no `@drop`.

```coral
import(lib) std::time { Timespec, nowMonotonic, subTimespec, sleepMs, timespecToF64 };

Timespec t0 = nowMonotonic();
sleepMs(10u);
Timespec t1 = nowMonotonic();
println(timespecToF64(subTimespec(t1, t0)));
```

### 33. `std::duration`, `Duration`

Ported from the old `std/core/duration` module. A `Duration` is a signed span of
time stored as `(i64 sec, i64 nsec)` and always normalized so
`0 <= nsec < 1_000_000_000`. Arithmetic saturates at the `i64` limits instead of
wrapping. The implementation is identical on Linux and Windows.

```coral
pub struct Duration
{
    i64 sec;
    i64 nsec;

    static Duration fromSecs(i64 s)
    static Duration fromMillis(i64 ms)
    static Duration fromMicros(i64 us)
    static Duration fromNanos(i64 ns)
    static Duration fromF64(f64 seconds)

    i64 asSecs()
    i64 asMillis()
    i64 asMicros()
    i64 asNanos()
    f64 asF64()
    bool isZero()

    Duration add(Duration other)
    Duration sub(Duration other)
    Duration mul(i64 factor)
    Duration div(i64 factor)        // assert(factor != 0)

    i32 compare(Duration other)     // -1 / 0 / 1
    bool eq(Duration other)
    bool lt(Duration other)
    bool gt(Duration other)
    bool le(Duration other)
    bool ge(Duration other)

    Timespec toTimespec()
    void     sleep()                // blocks for the span
}

pub Duration seconds(i64 s)
pub Duration millis(i64 ms)
pub Duration micros(i64 us)
pub Duration nanos(i64 ns)
```

- `fromF64` maps NaN and non-representable inputs to `Duration::fromSecs(0)`.
- `mul` / `div` and the scaled `as*` accessors return the saturated extreme on
  overflow rather than wrapping.
- `sleep()` bridges to `std::time::sleepTimespec`.

```coral
import(lib) std::duration { Duration, seconds, millis };

Duration total = seconds(2).add(millis(500));
println(total.asMillis());   // 2500
```

---

## std::math

### 34. `std::math::math`, libm bindings, constants, scalar helpers

```coral
pub extern f64 sin(f64 x)  cos(f64 x)  tan(f64 x)  sqrt(f64 x)  pow(f64 x, f64 y)
pub extern f64 floor(f64 x) ceil(f64 x) fabs(f64 x) asin(f64 x) acos(f64 x) atan(f64 x)
pub extern f64 atan2(f64 y, f64 x) sinh(f64 x) cosh(f64 x) tanh(f64 x) cbrt(f64 x)
pub extern f64 exp(f64 x) log(f64 x) log2(f64 x) log10(f64 x) round(f64 x)
pub extern f64 fmod(f64 x, f64 y) hypot(f64 x, f64 y) erf(f64 x) erfc(f64 x)
pub extern f64 tgamma(f64 x) lgamma(f64 x)

pub const f64 tau  = 6.28318530717958647692;
pub const f64 srt2 = 1.41421356237309504880;
pub const f64 pi   = 3.14159265358979323846;
pub const f64 e    = 2.71828182845904523536;

pub f64 piF()
pub f64 eF()
pub f64 sqrt2F()
pub f64 degToRad(f64 deg)
pub f64 radToDeg(f64 rad)

pub i64 clampI64(i64 v, i64 lo, i64 hi)
pub u64 clampU64(u64 v, u64 lo, u64 hi)
pub f64 clampF64(f64 v, f64 lo, f64 hi)
pub f64 lerp(f64 a, f64 b, f64 t)
pub f64 invLerp(f64 a, f64 b, f64 v)
pub f64 mapRange(f64 v, f64 a1, f64 b1, f64 a2, f64 b2)

pub i64 minI64(i64 a, i64 b)   maxI64(i64 a, i64 b)
pub u64 minU64(u64 a, u64 b)   maxU64(u64 a, u64 b)
pub f64 minF64(f64 a, f64 b)   maxF64(f64 a, f64 b)

pub u64 absI64(i64 x)
pub f64 absF64(f64 x)
pub i64 signI64(i64 x)
pub f64 signF64(f64 x)
pub bool isFinite(f64 x)
pub bool isNan(f64 x)

pub f64 add(f64 x, f64 y)
pub f64 sub(f64 x, f64 y)
pub f64 mul(f64 x, f64 y)
pub f64 div(f64 x, f64 y)
pub i64 truncF(f64 f)
```

### 35. `std::math::complex`, `Complex`

```coral
pub struct Complex
{
    f64 re;
    f64 im;

    static Complex new(f64 real, f64 imag)
    static Complex fromRe(f64 real)
    static Complex fromIm(f64 imag)

    Complex add(Complex other)
    Complex sub(Complex other)
    Complex mul(Complex other)
    Complex div(Complex other)
    Complex conj()
    Complex neg()
    Complex scale(f64 s)
    Complex exp()
    Complex log()
    Complex pow(Complex other)
    Complex sin()
    Complex cos()
    Complex sqrt()
    f64 abs()
    f64 arg()
    f64 absSq()
}
```

### 36. `std::math::matrix`, `Mat2`, `Mat3`, `Mat4`

```coral
pub struct Mat2
{
    f64 m[4];
    static Mat2 identity()
    static Mat2 fromRows(Vec2 r0, Vec2 r1)
    f64  at(usize row, usize col)
    void set(usize row, usize col, f64 val)
    Mat2 mul(Mat2 other)
    Vec2 mulVec(Vec2 v)
    Mat2 transpose()
    f64  det()
    Mat2 inverse()
}

pub struct Mat3
{
    f64 m[9];
    static Mat3 identity()
    static Mat3 fromRows(Vec3 r0, Vec3 r1, Vec3 r2)
    f64  at(usize row, usize col)
    void set(usize row, usize col, f64 val)
    Mat3 mul(Mat3 other)
    Vec3 mulVec(Vec3 v)
    Mat3 transpose()
    f64  det()
}

pub struct Mat4
{
    f64 m[16];
    static Mat4 identity()
    static Mat4 fromRows(Vec4 r0, Vec4 r1, Vec4 r2, Vec4 r3)
    static Mat4 translation(f64 tx, f64 ty, f64 tz)
    static Mat4 rotationX(f64 angle)
    static Mat4 rotationY(f64 angle)
    static Mat4 rotationZ(f64 angle)
    static Mat4 scale(f64 sx, f64 sy, f64 sz)
    static Mat4 perspective(f64 fov, f64 aspect, f64 near, f64 far)
    static Mat4 lookAt(Vec3 eye, Vec3 center, Vec3 up)
    f64  at(usize row, usize col)
    void set(usize row, usize col, f64 val)
    Mat4 mul(Mat4 other)
    Vec4 mulVec(Vec4 v)
    Mat4 transpose()
}
```

### 37. `std::math::vector`, `Vec2`, `Vec3`, `Vec4`

```coral
pub struct Vec2
{
    f64 x; f64 y;
    static Vec2 new(f64 x, f64 y)
    Vec2 add(Vec2 other)  sub(Vec2 other)  scale(f64 s)  normalize()  lerp(Vec2 other, f64 t)
    f64  dot(Vec2 other)  lengthSq()  length()
}

pub struct Vec3
{
    f64 x; f64 y; f64 z;
    static Vec3 new(f64 x, f64 y, f64 z)
    Vec3 add(Vec3 other)  sub(Vec3 other)  scale(f64 s)  cross(Vec3 other)  normalize()  lerp(Vec3 other, f64 t)
    f64  dot(Vec3 other)  lengthSq()  length()
}

pub struct Vec4
{
    f64 x; f64 y; f64 z; f64 w;
    static Vec4 new(f64 x, f64 y, f64 z, f64 w)
    Vec4 add(Vec4 other)  sub(Vec4 other)  scale(f64 s)  normalize()  lerp(Vec4 other, f64 t)
    f64  dot(Vec4 other)  lengthSq()  length()
}
```

### 38. `std::math::random`, RNGs

```coral
pub u64 nextU64()
pub u32 nextU32()
pub u64 nextRange(u64 lo, u64 hi)
pub f64 nextF64()          // seeded from /dev/urandom

pub struct XorShift32
{
    u32 state;
    XorShift32 seed(u32 s)
    u32 next()
    u64 nextU64()
    u64 nextRange(u64 lo, u64 hi)
}

pub struct Pcg32
{
    u64 state;
    u64 inc;
    Pcg32 seed(u64 initState, u64 initSeq)
    u32 next()
    u64 nextU64()
    u64 nextRange(u64 lo, u64 hi)
}
```

---

## std::fmt

### 39. `std::fmt::fmt`, String formatting

```coral
pub String format(str f, ...)                 // NOTE: stub, see below
pub String formatInt(i64 val, u64 radix, bool upper)
pub String formatUint(u64 val, u64 radix, bool upper)
pub String formatFloat(f64 val, u64 precision)
pub String formatHex(u64 val, bool prefix)
pub String formatHexUpper(u64 val, bool prefix)
pub String formatBin(u64 val, bool prefix)
pub String formatChar(char c)
pub String padLeft(str sv, usize width, u8 pad)
pub String padRight(str sv, usize width, u8 pad)
pub String repeat(str sv, usize count)
pub String join(const str* parts, usize count, str sep)
pub String joinVec(const Vec<String>* parts, str sep)
// helper: u64 _clampRadix(u64 radix)
```
> **Note:** `fmt::format` currently strips `{}` placeholders without
> substituting arguments; use `io::ios`' `print`/`println` (whose format
> handling is implemented in the compiler) for real formatting.

---

## std::io

### 40. `std::io::ios`, Console I/O and parsing (prelude)

```coral
// formatting / output
pub void print<comptime T>(T fmt, ...)
pub void println<comptime T>(T fmt, ...)
pub void eprint<comptime T>(T fmt, ...)
pub void eprintln<comptime T>(T fmt, ...)
pub void vaprint(... args)
pub void flush()

// formatting helpers passed as arguments
pub struct Spaces { u64 count; }
pub struct Repeat { u8 ch; u64 count; }
pub struct Hex    { u64 value; }
pub struct Bin    { u64 value; }
pub struct Fixed  { f64 value; u64 precision; }
pub Spaces spaces(u64 count)
pub Repeat repeat(u8 ch, u64 count)
pub Hex    hex(u64 value)
pub Bin    bin(u64 value)
pub Fixed  fixed(f64 value, u64 precision)

// parsing
pub i64 parseI64(str sv, bool* ok)
pub u64 parseU64(str sv, bool* ok)
pub f64 parseF64(str sv, bool* ok)

// input
pub u8   readChar()
pub bool readLine(String* out)
pub void read<comptime T>(T* out)
pub T    readVal<T>()
```

### 41. `std::io::fs`, Filesystem

```coral
pub variant IoError
{
    Os       { i32 code; str op; },   // errno / GetLastError
    Eof      { str op; },             // stream ended early
    BadUsage { str msg; }             // caller-side problem
}
pub extend IoError
{
    static IoError os(str op)
}

pub const i32 O_RDONLY = 0;   O_WRONLY = 1;  O_RDWR = 2;
pub const i32 O_CREAT  = 64;  O_TRUNC  = 512; O_APPEND = 1024;
pub const i32 S_IRWXU  = 448; S_IRUSR  = 256; S_IWUSR = 128; S_IXUSR = 64;
pub const i32 SEEK_SET = 0;   SEEK_CUR = 1;   SEEK_END = 2;
pub const i32 F_OK = 0; R_OK = 4; W_OK = 2; X_OK = 1;

pub distinct File = i32;
pub distinct Dir  = rawptr;

pub struct Stat
{
    u64 st_dev; u64 st_ino; u64 st_nlink;
    u32 st_mode; u32 st_uid; u32 st_gid; u32 pad0;
    u64 st_rdev; i64 st_size; i64 st_blksize; i64 st_blocks;
    i64 st_atime; i64 st_atimeNsec;
    i64 st_mtime; i64 st_mtimeNsec;
    i64 st_ctime; i64 st_ctimeNsec;
    i64 reserved[3];
}

pub enum FileType { Unknown, Regular, Directory, CharDevice, BlockDevice, Fifo, Symlink, Socket }

pub Result<File, IoError> fileOpen(str path, str mode)
pub void   fileClose(File f)
pub Result<isize, IoError> fileRead(File f, u8* buf, usize count)
pub Result<isize, IoError> fileWrite(File f, const u8* buf, usize count)
pub Result<isize, IoError> fileSeek(File f, isize offset, i32 whence)
pub bool   fileExists(str path)
pub Option<bool> statPath(str path, Stat* out)
pub FileType getFileType(const Stat* s)
pub Result<bool, IoError> createDir(str path, i32 mode)
pub Result<bool, IoError> createDirRecursive(str path, i32 mode)
pub Result<bool, IoError> removeDir(str path)
pub Result<bool, IoError> deleteFile(str path)
pub Result<bool, IoError> renameFile(str oldPath, str newPath)
pub bool   canAccess(str path, i32 mode)
pub Result<Dir, IoError> openDir(str path)
pub rawptr readDir(Dir dir)
pub void   closeDir(Dir dir)
pub Result<String, IoError> readFileToString(str path)
pub Result<bool, IoError>   writeFileFromString(str path, const String* data)

pub struct Dirent
{
    u64 d_ino; i64 d_off; u16 d_reclen; u8 d_type; u8 d_name[256];
}
pub bool readDirEntry(Dir dir, Dirent* out)
```

### 42. `std::io::bio`, Binary readers/writers

```coral
const i32 SEEK_SET = 0;
const i32 SEEK_CUR = 1;

pub struct FileReader
{
    i32 fd;
    static FileReader fromFd(File fd)
    Result<bool, IoError> readBytes(u8* dst, u64 n)   // exactly n bytes
    u8   readU8()
    i8   readI8()
    u16  readU16Le()  readU16Be()
    i16  readI16Le()  readI16Be()
    u32  readU32Le()  readU32Be()
    i32  readI32Le()  readI32Be()
    u64  readU64Le()  readU64Be()
    i64  readI64Le()  readI64Be()
    f32  readF32Le()  readF32Be()
    f64  readF64Le()  readF64Be()
    void skip(u64 n)
}

pub struct FileWriter
{
    i32 fd;
    static FileWriter fromFd(File fd)
    void writeU8(u8 v)
    void writeI8(i8 v)
    void writeU16Le(u16 v)  writeU16Be(u16 v)
    void writeI16Le(i16 v)  writeI16Be(i16 v)
    void writeU32Le(u32 v)  writeU32Be(u32 v)
    void writeI32Le(i32 v)  writeI32Be(i32 v)
    void writeU64Le(u64 v)  writeU64Be(u64 v)
    void writeI64Le(i64 v)  writeI64Be(i64 v)
    void writeF32Le(f32 v)  writeF32Be(f32 v)
    void writeF64Le(f64 v)  writeF64Be(f64 v)
    Result<bool, IoError> writeBytes(const u8* src, u64 n)   // exactly n bytes
}

pub u16 bswapU16(u16 v)
pub u32 bswapU32(u32 v)
pub u64 bswapU64(u64 v)
```

### 43. `std::io::fios`, `FILE*`-based I/O

```coral
pub distinct FileHandle = rawptr;

pub Result<FileHandle, IoError> fileOpen(str path, str mode)
pub void   fileClose(FileHandle fh)
pub Result<usize, IoError> fileWrite(FileHandle fh, str data)
pub Result<usize, IoError> fileRead(FileHandle fh, u8* buf, usize maxLen)
pub bool   fileEof(FileHandle fh)
pub bool   fileError(FileHandle fh)
pub void   fileFlush(FileHandle fh)
pub Result<usize, IoError> fileWriteString(FileHandle fh, const String* s)
pub Result<bool, IoError>  fileReadAll(str path, String* out)
```

### 44. `std::io::log`, `Logger`

```coral
pub variant LogLevel { Debug, Info, Warn, Error, Fatal }

pub struct Logger
{
    LogLevel minLevel;
    String name;

    static Logger new(str name, LogLevel minLevel)
    void dispose()
    void setLevel(LogLevel level)
    bool enabled(LogLevel level)
    void debug(str msg)
    void info(str msg)
    void warn(str msg)
    void error(str msg)
    void fatal(str msg)
    // helper: void _log(LogLevel level, str msg)
}
```

### 45. `std::io::net`, TCP/UDP sockets

```coral
const i32 AF_INET = 2;  SOCK_STREAM = 1;  SOCK_DGRAM = 2;
const i32 IPPROTO_TCP = 6; IPPROTO_UDP = 17;
const i32 SOL_SOCKET = 1; SO_REUSEADDR = 2;

pub struct sockaddr_in
{
    u16 sinFamily; u16 sinPort; u32 sinAddr; u8 sinZero[8];
}

pub distinct TcpSocket = i32;
pub Result<TcpSocket, IoError> tcpConnect(str ip, u16 port)
pub Result<TcpSocket, IoError> tcpListen(u16 port)
pub Result<TcpSocket, IoError> tcpAccept(TcpSocket server)
pub Result<isize, IoError>     tcpSend(TcpSocket sock, const u8* buf, usize len)
pub Result<isize, IoError>     tcpRecv(TcpSocket sock, u8* buf, usize len)
pub void tcpClose(TcpSocket sock)

pub struct UdpSocket { i32 fd; }
pub Result<UdpSocket, IoError> udpSocket()
pub Result<bool, IoError>      udpBind(UdpSocket* s, u16 port)
pub Result<isize, IoError>     udpSendTo(UdpSocket* s, const u8* buf, usize len, str ip, u16 port)
pub Result<isize, IoError>     udpRecvFrom(UdpSocket* s, u8* buf, usize len)
pub void udpClose(UdpSocket* s)
```

### 46. `std::io::path`, Path manipulation

```coral
const u8 SEP = '/';
const u8 ALT_SEP = '\\';

pub usize  findLastSep(str p)
pub bool   isAbsolute(str p)
pub bool   hasExtension(str p)
pub str    extension(str p)
pub str    stem(str p)
pub str    parent(str p)
pub str    filename(str p)
pub String join(str a, str b)
pub String normalize(str p)
pub String absolute(str base, str rel)
pub String changeExtension(str p, str newExt)
```

### 47. `std::io::process`, Subprocesses

```coral
pub struct Process
{
    i32 pid;
    i32 stdinFd;
    i32 stdoutFd;
    i32 stderrFd;
}

pub struct ProcessResult
{
    i32  exitCode;
    bool signaled;
    i32  termSignal;
}

pub struct pollfd { i32 fd; i16 events; i16 revents; }

pub Result<Process, IoError>       spawn(str cmd, Vec<str>* args)
pub Result<ProcessResult, IoError> waitFor(Process* p)
pub Result<isize, IoError>         writeStdin(Process* p, const cchar* data, usize len)
pub Result<isize, IoError>         readStdout(Process* p, u8* buf, usize maxLen)
pub Result<isize, IoError>         readStderr(Process* p, u8* buf, usize maxLen)
pub Result<i32, IoError>           run(str cmd, Vec<str>* args)
pub void                           exit(i32 code)
```

### 48. `std::io::temp`, Temporary files/dirs

```coral
pub struct TempFile
{
    i32 fd;
    String path;
    bool autoDelete;
    static Result<TempFile, IoError> create(str prefix, str suffix)
    void dispose()
    File fd()
    str  pathStr()
    void setAutoDelete(bool ad)
}

pub struct TempDir
{
    String path;
    bool autoDelete;
    static Result<TempDir, IoError> create(str prefix)
    void dispose()
    str  pathStr()
    void setAutoDelete(bool ad)
    bool isValid()
}

pub extend TempFile : @drop { void drop(); }
pub extend TempDir  : @drop { void drop(); }
```

### 49. `std::io::term`, ANSI terminal control

```coral
pub void reset()
pub void bold()   dim()   italic()   underline()   blink()   reverse()
pub void hidden() strikethrough()

pub void black()  red()  green()  yellow()  blue()  magenta()  cyan()  white()
pub void bgBlack() bgRed() bgGreen() bgYellow() bgBlue() bgMagenta() bgCyan() bgWhite()
pub void brightBlack() brightRed() brightGreen() brightYellow()
pub void brightBlue() brightMagenta() brightCyan() brightWhite()

pub void cursorUp(u64 n)
pub void cursorDown(u64 n)
pub void cursorRight(u64 n)
pub void cursorLeft(u64 n)
pub void cursorPos(u64 row, u64 col)

pub void clearScreen()
pub void clearLine()
pub void clearToEnd()
pub void clearLineEnd()
pub void saveCursor()
pub void restoreCursor()
pub void hideCursor()
pub void showCursor()
// helpers: bool _isTty(); void _writeCSI(str code); void _writeStr(str s);
//           u64 _clampN(u64 n)
```

### 50. `std::io::cmd`, `ArgParser`

```coral
pub struct ArgParser
{
    Vec<String> positional;
    bool   error;
    String errMsg;
    usize  pos;

    static ArgParser new()
    void dispose()
    void parse(i32 argc, cchar** argv)
    bool hasFlag(i32 argc, cchar** argv, str shortFlag, str longFlag)
    bool getOption(i32 argc, cchar** argv, str shortFlag, str longFlag, String* out)
    usize count()
    str   get(usize idx)
    // helper: bool _afterDoubleDash(i32 argc, cchar** argv, i32 idx)
}
pub Option<str> commandLine()
```

### 51. `std::io::env`, Environment variables

```coral
pub Option<String> get(str name)
pub bool getInto(str name, String* out)
pub Result<bool, IoError> set(str name, str value)
pub Result<bool, IoError> unset(str name)
pub usize all(Vec<String>* out)
```

---

## std::memory

### 52. `std::memory::mman`, Allocators and allocation (aka `std::mman`)

```coral
pub variant AllocError { AllocFailed { str msg; } }

pub Allocator* defaultAllocator;          // global default allocator
pub void initDefaultAllocator()
pub void ensureDefaultAllocator()
pub void deinitDefaultAllocator()

pub Allocator libcAllocator;              // malloc/free-backed
pub Allocator miAllocator;                // mimalloc-backed
pub Allocator cAllocator;                 // libc-backed wrapper
pub Allocator pageAllocator;              // page-granular
pub const usize pageSize = 4096u;

pub struct FixedBufferAllocator
{
    u8* buffer; usize cap; usize used;
    void init(u8* buffer, usize size)
    Allocator allocator()
    void reset()
    usize remaining(const self*)
}

pub struct StackFallbackAllocator
{
    FixedBufferAllocator fba;
    Allocator* fallback;
    u8 stackBuf[1024];
    void init(Allocator* fallback)
    Allocator allocator()
}

pub struct ArenaAllocator
{
    Allocator* backing;
    u8* base; usize cap; usize used;
    void init(Allocator* backing, usize initialCap)
    void deinit()
    Allocator allocator()
    rawptr push(usize size)
    T*     pushType<T>(usize count)
    void   reset()
    usize  remaining()
}

pub struct PoolAllocator
{
    rawptr freeList; usize blockSize; usize blockCount;
    u8* backing; Allocator* source;
    void init(Allocator* source, usize blockSize, usize blockCount)
    void deinit()
    Allocator allocator()
    rawptr allocBlock()
    void   freeBlock(rawptr block)
}

pub struct ScopeAlloc
{
    Allocator* backing;
    rawptr* ptrs; usize* sizes;
    usize len; usize cap;
    void init(Allocator* backing, usize cap)
    rawptr alloc(usize size)
    T*     allocType<T>(usize count)
    void   freeAll()
    void   deinit()
    usize  bytesUsed(const self*)
    // helper: void _grow()
}

pub struct LoggingAllocator
{
    Allocator* parent;
    usize totalAlloced; usize totalFreed; usize currentUsed;
    usize allocCount; usize freeCount;
    rawptr* trackPtrs; usize* trackSizes;
    usize trackLen; usize trackCap;
    void init(Allocator* parent)
    Allocator allocator()
    void printStats()
    // helpers: _trackGrow _track _untrack
}

// convenience wrappers over the default allocator
pub T*   alloc<T>(usize count)
pub void dealloc<T>(T* ptr)
pub T*   realloc<T>(T* ptr, usize newCount)
pub void copy<T>(T* dst, T* src, usize count)
pub void move<T>(T* dst, T* src, usize count)
pub void zero<T>(T* ptr, usize count)
pub bool equal<T>(const T* a, const T* b, usize count)
```

### 53. `std::memory::intrinsics::memory`, Raw memory primitives

```coral
pub void memmove(rawptr dst, const rawptr src, usize n)
pub void memcpy(rawptr dst, const rawptr src, usize n)
pub rawptr mmap(rawptr addr, usize length, i32 prot, i32 flags, i32 fd, i64 offset)
pub void munmap(rawptr addr, usize length)
pub void memset(rawptr dst, u8 val, usize n)
pub i32  memcmp(const rawptr a, const rawptr b, usize n)
```

### 54. `std::memory::allocators::allocator`, `Allocator` (vtable)

```coral
pub struct Allocator
{
    rawptr ctx;
    rawptr(rawptr, usize)          alloc;
    void(rawptr, rawptr)           free;
    rawptr(rawptr, rawptr, usize)  realloc;
}
```

### 55. `std::memory::allocators::tlsf`, `Tlsf` (Two-Level Segregated Fit)

```coral
pub struct Tlsf
{
    rawptr heapStart; rawptr heapEnd; usize heapSize;
    FreeBlock* freeLists[32][32];
    u32 fliBitmap;
    u32 sliBitmap[32];

    void init(rawptr heap, usize size)
    rawptr alloc(usize size)
    void   free(rawptr ptr)
    rawptr realloc(rawptr ptr, usize newSize)
    usize  getHeapSize(const self*)
    usize  getFreeSize(const self*)
    Allocator allocator()
    // helpers: _fls _lsbIndex _getIndex _blockSize _blockFromPtr _memcpy
    //          _ptrFromBlock _nextBlock _writeFooter _prevBlock
    //          _removeFree _insertFree _findSuitableBlock
}
```
Constants: `FLI_COUNT = 32`, `SLI_COUNT = 32`, `MIN_BLOCK_SIZE = 32u`,
`BLOCK_ALIGN = 8u`, `BLOCK_USED = 1u`, `BLOCK_PREV_USED = 2u`.

### 56. `std::memory::allocators::mimalloc`, `MiAlloc`

```coral
pub struct MiAlloc
{
    MiHeap heap;

    void init(usize reserveSize)
    rawptr alloc(usize size)
    void   free(rawptr ptr)
    rawptr realloc(rawptr ptr, usize newSize)
    rawptr calloc(usize count, usize size)
    usize  getAllocated()
    usize  getFreed()
    usize  getUsed()
    usize  getMapped()
    Allocator allocator()
}
pub void miStatsPrint(MiAlloc* alloc)
```
Constants include `MI_ARENA_SIZE = 64 MiB`, `MI_SEGMENT_SIZE = 4 MiB`,
`MI_PAGE_SIZE = 64 KiB`, `MI_SLICE_SIZE = 64 KiB`, `MI_ALIGN = 16`,
`MI_MAX_BLOCK_SIZE = 512 KiB`, `MI_HUGE_THRESHOLD = 128 KiB`,
`MI_SIZE_CLASS_COUNT = 44`, `MI_SEGMENT_MAP_SIZE = 64`.

### 57. `std::memory::pool`, `Pool<T>` (fixed-size object pool)

```coral
pub struct Pool<T>
{
    rawptr freeList;
    u8* blocks;
    usize blockSize;
    usize blockCount;
    usize totalBlocks;
    usize usedBlocks;

    static Pool<T> new()
    void dispose()
    T*   acquire()
    void release(T* obj)
    usize available()
    usize used()
    usize capacity()
    bool _grow()
}
```

### 58. `std::memory::shared_ptr`, `SharedPtr<T>` (refcounted)

```coral
pub struct SharedPtr<T>
{
    T* ptr;
    RefCount* rc;       // contains usize count

    bool init(T value)
    void dispose()
    T    get(const self*)
    T*   data()
    const T* constData(const self*)
    usize refCount(const self*)
    bool isValid(const self*)
}
void drop()
```

### 59. `std::memory::smart_ptr`, `SmartPtr<T>` (unique)

```coral
pub struct SmartPtr<T>
{
    T* ptr;

    bool init(T value)
    void dispose()
    T    get(const self*)
    T*   data()
    const T* constData(const self*)
    void set(T value)
    bool isValid(const self*)
    T    take()
}
void drop()
```

---

## std::concurrent

### 60. `std::concurrent::mutex`, `Mutex`

```coral
pub struct Mutex
{
    rawptr impl[6];
    void init()
    void initRecursive()
    void destroy()
    void lock()
    void unlock()
    bool tryLock()
}
```

### 61. `std::concurrent::rwlock`, `RwLock`

```coral
pub struct RwLock
{
    rawptr impl[8];
    void init()
    void destroy()
    void readLock()
    void writeLock()
    bool tryReadLock()
    bool tryWriteLock()
    void unlock()
}
```

### 62. `std::concurrent::semaphore`, `Semaphore`

```coral
pub struct Semaphore
{
    rawptr impl[8];
    bool init(u32 value)
    void destroy()
    void wait()
    bool tryWait()
    void post()
    i32  value()
}
```

### 63. `std::concurrent::signal`, POSIX signals

```coral
pub const i32 SIGABRT = 6;  SIGALRM = 14; SIGBUS = 7;  SIGCHLD = 17;
pub const i32 SIGCONT = 18; SIGFPE = 8;   SIGHUP = 1;  SIGILL = 4;
pub const i32 SIGINT = 2;   SIGKILL = 9;  SIGPIPE = 13; SIGQUIT = 3;
pub const i32 SIGSEGV = 11; SIGSTOP = 19; SIGTERM = 15; SIGTSTP = 20;
pub const i32 SIGTTIN = 21; SIGTTOU = 22; SIGUSR1 = 10; SIGUSR2 = 12;
pub const i32 SIGSYS = 31;  SIGTRAP = 5;  SIGURG = 23; SIGXCPU = 24; SIGXFSZ = 25;
pub const u8 SIG_DFL = 0;
pub const usize SIG_IGN = 1;

pub rawptr handle(i32 sig, rawptr handler)
pub void   ignore(i32 sig)
pub void   defaultHandler(i32 sig)
pub i32    sendSig(i32 pid, i32 sig)
pub i32    raiseSig(i32 sig)
```

### 64. `std::concurrent::thread`, Threads, conditions, atomics

```coral
pub distinct Thread = rawptr;

pub struct ConditionVar
{
    rawptr impl[6];
    void init()
    void destroy()
    void wait(Mutex* mutex)
    void signal()
    void broadcast()
}

pub variant ThreadError { CreateFailed { str msg; } }

pub Result<Thread, ThreadError> threadCreate(rawptr(rawptr) fn, rawptr arg)
pub bool   threadJoin(Thread t, rawptr* retval)
pub void   threadExit(rawptr retval)
pub Thread threadCurrent()

pub struct AtomicU64
{
    u64 value;
    u64  load()
    void store(u64 val)
    u64  fetchAdd(u64 delta)
    u64  fetchSub(u64 delta)
    bool compareExchange(u64 expected, u64 desired)
}

pub struct AtomicU32
{
    u32 value;
    u32  load()
    void store(u32 val)
    u32  fetchAdd(u32 delta)
    u32  fetchSub(u32 delta)
    bool compareExchange(u32 expected, u32 desired)
}
```

### 65. `std::concurrent::threadpool`, `ThreadPool`

```coral
pub struct ThreadPool
{
    Mutex mutex;
    ConditionVar cond;
    Thread* threads;
    Task* queueHead;
    Task* queueTail;
    u32 threadCount;
    bool stop;

    bool init(u32 numThreads)
    void deinit()
    bool enqueue(void(rawptr) func, rawptr arg)
    u32  threadCount()
    // helper: void _worker()
}
pub extend ThreadPool : @drop { void drop(); }
// helper: void _workerEntry(rawptr arg)
```

### 66. `std::concurrent::async`, Stackful-fiber async runtime

Built on glibc `ucontext`. `spawn` creates a fiber, `await` parks the current
fiber until a future resolves, and `run`/`runOnce` drive the scheduler.

```coral
pub variant AsyncError
{
    OutsideFiber { str msg; },
    NullFuture   { str msg; },
    SpawnFailed  { str msg; }
}

pub struct Future
{
    u8     state;         // FUTURE_PENDING / FUTURE_READY
    rawptr result;
    Fiber* waiters;
    Future* chanNext;
    bool   counted;
}

pub usize defaultFiberStackSize = 131072;   // 128 KiB

pub bool init()
pub Result<Future*, AsyncError> spawn(void(rawptr) fn, rawptr arg)
pub Result<rawptr, AsyncError>  await(Future* f)
pub Future* sleep(u64 ms)
pub bool    run()
pub void    runOnce()
pub Future* poolRun(ThreadPool* pool, void(rawptr) fn, rawptr arg)

pub struct AsyncChannel
{
    rawptr* buf;
    usize cap;
    usize count;
    usize head;
    Future* recvHead;
    Future* recvTail;

    bool    init(usize capacity)
    void    deinit()
    bool    send(rawptr value)
    Future* recv()
}
pub extend AsyncChannel : @drop { void drop(); }
```
State/step constants (`FUTURE_*`, `FIBER_*`, `STEP_*`) and the scheduler
internals (`Fiber`, `Scheduler`, `TimerEntry`, `_nowMs`, `_initScheduler`, …)
are non-`pub` and not part of the public surface.

---

## std::crypto

### 67. `std::crypto::aes`, AES-256 / AES-128

```coral
pub struct Aes256
{
    u8  roundKeys[240];
    u32 nRounds;
    void init(const u8* key)
    void encryptBlock(u8* block)
    void decryptBlock(u8* block)
    bool encryptCbc(const u8* iv, u8* data, usize len)
    bool decryptCbc(const u8* iv, u8* data, usize len)
}

pub struct Aes128
{
    u8  roundKeys[176];
    u32 nRounds;
    void init(const u8* key)
    void encryptBlock(u8* block)
    void decryptBlock(u8* block)
    bool encryptCbc(const u8* iv, u8* data, usize len)
    bool decryptCbc(const u8* iv, u8* data, usize len)
}
```
Round constants/tables (`SBOX`, `RSBOX`, `RCON`) and the block-step helpers are
module-private.

### 68. `std::crypto::base64`, Base64 (`+/` alphabet)

```coral
pub usize  encodeB64(const u8* src, usize srcLen, u8* dst, usize dstCap)
pub String encodeToString(const u8* src, usize srcLen)
pub usize  decode(str src, u8* dst, usize dstCap)
```

### 69. `std::crypto::bloom`, Bloom filter

```coral
pub struct Bloom
{
    Vec<u64> bits;
    usize numBits;
    usize numHashes;

    static Bloom new(usize numBits, usize numHashes)
    void dispose()
    void insert(str data, usize len)
    bool contains(str data)
    void clear()
    usize bitsCount()
    // helper: u64 _hash(str data, u64 seed)
}
```

### 70. `std::crypto::crc`, CRC-32 / CRC-64

```coral
pub u32 crc32(str data)
pub u64 crc64(str data)
```

### 71. `std::crypto::hash`, Generic hash functions

```coral
pub u64 fnv1a(const u8* data, usize len)
pub u64 fnv1aStr(str s)
pub u32 murmur3(const u8* data, usize len, u32 seed)
pub u64 wyhash(const u8* data, usize len, u64 seed)
pub u64 wyhashStr(str s)
pub u64 hashCombine(u64 seed, u64 value)
```

### 72. `std::crypto::hex`, Hex encoding

```coral
pub usize  encodeHx(str src, String dst)
pub String encodeToString(str src)
pub usize  decode(str src, String dst)
pub bool   isValid(str src)
```

### 73. `std::crypto::hmac`, HMAC-SHA256

```coral
const u64 BLOCK_SIZE = 64;
const u64 HASH_SIZE  = 32;

pub struct HmacSha256
{
    u8   keyBlock[BLOCK_SIZE];
    bool initialized;

    void init(const u8* key, usize keyLen)
    void compute(const u8* msg, usize msgLen, u8* outDigest)
    void computeWithKey(const u8* key, usize keyLen, const u8* msg, usize msgLen, u8* outDigest)
    bool verify(const u8* msg, usize msgLen, const u8* expectedDigest)
}
pub void hmacSha256(const u8* key, usize keyLen, const u8* msg, usize msgLen, u8* outDigest)
```

### 74. `std::crypto::sha256`, SHA-256

```coral
pub struct Sha256
{
    u32 state[8];
    u8  buf[64];
    u64 count;
    u64 bitLen;

    void init()
    void update(const u8* data, usize len)
    void final(u8* digest)
    // helper: void _transform()
}
pub void hash(const u8* data, usize len, u8* digest)
```

---

## std::parser

### 75. `std::parser::csv`, `CsvReader`

```coral
pub variant ParseError
{
    Syntax   { str msg; u32 line; u32 col; },
    Semantic { str msg; }
}

pub struct CsvReader
{
    const u8* data;
    usize len;
    usize pos;
    usize line;
    bool  error;
    str   errMsg;
    u8    delim;

    static CsvReader new(str input)
    bool eof()
    Result<bool, ParseError> readRow(Vec<String>* fields)
    // helpers: void fail(str msg); ParseError err(); bool _readField(String* out)
}
```

### 76. `std::parser::ini`, `IniFile` / `IniSection`

```coral
pub struct IniSection
{
    HashMap<String, String> entries;

    static IniSection new()
    void dispose()
    Option<String> get(str key)
    void set(str key, str value)
}

pub struct IniFile
{
    Vec<IniSection> sections;
    Vec<String>     names;

    static IniFile new()
    void dispose()
    void parse(str input)                  // lenient; cannot fail
    Option<IniSection*> section(str name)
    Option<String> get(str section, str key)
}

pub extend IniSection : @drop { void drop(); }
pub extend IniFile    : @drop { void drop(); }
```

### 77. `std::parser::json`, `JsonValue`

```coral
pub variant ParseError
{
    Syntax   { str msg; u32 line; u32 col; },
    Semantic { str msg; }
}
pub enum JsonType { Null, Bool, I64, F64, String, Array, Object }

pub struct JsonValue
{
    JsonType type;
    bool  boolVal;
    i64   i64Val;
    f64   f64Val;
    String strVal;
    Vec<JsonValue> arrVal;
    Vec<JsonPair>  objVal;

    static JsonValue nullVal()
    static JsonValue boolVal(bool b)
    static JsonValue i64Val(i64 n)
    static JsonValue f64Val(f64 n)
    static JsonValue stringVal(String s)
    static JsonValue arrayVal()
    static JsonValue objectVal()
    void dispose()
}

pub struct JsonPair { String key; JsonValue value; }

pub Result<JsonValue, ParseError> parseJson(str input)
pub String serialize(JsonValue* v)
pub extend JsonValue : @drop { void drop(); }
```

### 78. `std::parser::toml`, `TomlDoc`

```coral
pub variant ParseError
{
    Syntax   { str msg; u32 line; u32 col; },
    Semantic { str msg; }
}
pub enum TomlValueType { String, Integer, Float, Bool, Array, Table }

pub struct TomlValue
{
    TomlValueType type;
    String strVal;
    i64    intVal;
    f64    floatVal;
    bool   boolVal;
    Vec<TomlValue> arrVal;
    Vec<TomlPair>  tableVal;

    static TomlValue stringVal(str s)
    static TomlValue intVal(i64 n)
    static TomlValue floatVal(f64 n)
    static TomlValue boolVal(bool b)
    static TomlValue arrayVal()
    static TomlValue tableVal()
    void dispose()
}

pub struct TomlPair { String key; TomlValue value; }

pub struct TomlDoc
{
    Vec<TomlPair> root;
    static TomlDoc new()
    void dispose()
    Option<TomlValue*> get(str key)
    Option<TomlValue*> getIn(str table, str key)
}

pub Result<TomlDoc, ParseError> parseToml(str input)
pub extend TomlValue : @drop { void drop(); }
pub extend TomlDoc   : @drop { void drop(); }
```

### 79. `std::parser::uuid`, `Uuid`

```coral
pub variant ParseError
{
    Syntax   { str msg; u32 line; u32 col; },
    Semantic { str msg; }
}

pub struct Uuid
{
    u8 bytes[16];
    static Uuid zero()
    static Uuid v4()
    static Result<Uuid, ParseError> fromString(str s)
    String toString()
    String toHex()
    bool eq(Uuid other)
    bool isNil()
}
pub String uuidV4()
pub Result<Uuid, ParseError> parseUuid(str s)
```

### 80. `std::parser::xml`, `XmlNode`

```coral
pub variant ParseError
{
    Syntax   { str msg; u32 line; u32 col; },
    Semantic { str msg; }
}
pub enum XmlNodeType { Element, Text, Comment, CData }

pub struct XmlAttribute
{
    String name;
    String value;
    void dispose()
}

pub struct XmlNode
{
    XmlNodeType type;
    String tag;
    String text;
    Vec<XmlAttribute> attrs;
    Vec<XmlNode>      children;

    static XmlNode element(str tag)
    static XmlNode text(str content)
    void dispose()
    bool hasAttr(str name)
    Option<str> getAttr(str name)
    Option<XmlNode*> firstChild(str tagName)
}

pub Result<XmlNode, ParseError> parseXml(str input)
pub String serializeXml(XmlNode* node)
pub extend XmlNode : @drop { void drop(); }
```

### 81. `std::parser::crlb`, Coral build-manifest parser
> Exists at `parser/crlb.crl` but is **not** re-exported by `parser/lib.crl`;
> import it directly.

```coral
pub variant ParseError
{
    Syntax   { str msg; u32 line; u32 col; },
    Semantic { str msg; }
}
pub enum CrbKind { Int, Bool, Str, List }

pub struct CrbValue
{
    CrbKind kind;
    i64    intVal;
    bool   boolVal;
    String strVal;
    Vec<CrbValue> listVal;

    static CrbValue intVal(i64 n)
    static CrbValue boolVal(bool b)
    static CrbValue stringVal(str s)
    static CrbValue listVal()
    void dispose()
}

pub struct CrbEntry { String key; CrbValue value; }

pub struct CrbBuild
{
    String name;
    String extends;          // empty if no extends clause
    Vec<CrbEntry> entries;
    Option<CrbValue*> get(str key)
    void dispose()
}

pub struct CrbManifest
{
    Vec<CrbEntry> top;       // schema / strict / other top-level keys
    Vec<CrbBuild> builds;

    static CrbManifest new()
    Option<CrbValue*> get(str key)
    Option<CrbBuild*> findBuild(str name)
    void dispose()
}

pub Result<CrbManifest, ParseError> parseCrlb(str input)
pub extend CrbValue    : @drop
pub extend CrbBuild    : @drop
pub extend CrbManifest : @drop
```

---

## misc / testing

### 82. `std::misc::erased`, `Erased` (type erasure)

```coral
pub struct Erased
{
    rawptr p;
    rawptr ptr()
    bool isNull()
    T* asPtr<T>()
}
pub Erased wrap(rawptr value)
```

### 83. `std::misc::cast`, `cast<T>`

```coral
pub T cast<T>(Erased val)     // reinterprets the wrapped pointer as T
```

### 84. `std::testing::test`, Test harness helpers

```coral
pub struct TestResult { str name; bool passed; str message; }

pub void _testBegin(str name)
pub void _testEnd()
pub void _testFail(str msg)
pub void assertEq(usize expected, usize actual, str msg)
pub void assertEqStr(str expected, str actual, str msg)
pub void assertTrue(bool cond, str msg)
pub void assertFalse(bool cond, str msg)
pub void assertNull(rawptr ptr, str msg)
pub void assertNotNull(rawptr ptr, str msg)
pub void testSummary()
pub bool testAllPassed()
```
