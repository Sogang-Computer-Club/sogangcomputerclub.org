<script lang="ts">
    import { goto } from '$app/navigation';
    import { login } from '$lib/api';
    import SGCC_cute from '$lib/assets/images/sgcc-cute.png';

    let email = $state('');
    let password = $state('');
    let error = $state('');
    let isLoading = $state(false);

    async function handleSubmit(event: Event) {
        event.preventDefault();
        error = '';
        isLoading = true;

        try {
            const result = await login({ email, password });
            // Store token in localStorage
            localStorage.setItem('access_token', result.access_token);
            // Redirect to home page
            await goto('/');
        } catch (e) {
            error = e instanceof Error ? e.message : 'Login failed';
        } finally {
            isLoading = false;
        }
    }
</script>

<main>
    <!-- Mobile view -->
    <div class="tablet:hidden bg-black text-white min-h-screen flex flex-col items-center px-6">
        <!-- Background image placeholder -->
        <div class="inset-0 w-full h-full opacity-50 bg-no-repeat bg-cover bg-center"
        style="background-image: url('');">
        </div>

        <!-- Login form -->
        <form onsubmit={handleSubmit} class="flex flex-col items-center mt-[calc(15vh)] relative z-10 w-full max-w-sm bg-[#252525] rounded-[20px] py-8">
            <!-- Logo -->
            <img alt="SGCC Symbol" src={SGCC_cute} class="absolute w-[80px] h-[80px] mb-4">
            <h1 class="text-[25px] font-normal mb-9">Login</h1>

            <!-- Error message -->
            {#if error}
                <div class="mb-4 px-12 w-full">
                    <p class="text-red-400 text-sm text-center">{error}</p>
                </div>
            {/if}

            <!-- Email input -->
            <div class="mb-6 w-full px-12">
                <label for="email" class="block text-[15px] font-sogang mb-2">이메일 주소</label>
                <input
                    id="email"
                    type="email"
                    bind:value={email}
                    required
                    disabled={isLoading}
                    class="w-full h-8 px-3 text-base text-black border-[#AE1F1F] border-2 rounded-full">
            </div>

            <!-- Password input -->
            <div class="mb-8 w-full px-12">
                <label for="password" class="block text-[15px] font-sogang mb-2">비밀번호</label>
                <input
                    id="password"
                    type="password"
                    bind:value={password}
                    required
                    disabled={isLoading}
                    class="w-full h-8 px-3 text-base text-black border-[#AE1F1F] border-2 rounded-full">
            </div>

            <!-- Login button -->
            <div class="flex w-21 h-8 justify-center mb-6">
                <button
                    type="submit"
                    aria-label="login"
                    disabled={isLoading}
                    class="bg-[#AE1F1F] w-full pt-1 rounded-full text-[18px] font-sogang disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#8a1919] transition-colors">
                    {isLoading ? '로그인 중...' : '로그인'}
                </button>
            </div>

            <!-- Bottom links -->
            <div class="w-full px-12 flex justify-between">
                <a href="/find" class="text-[10px] text-white font-normal hover:underline">비밀번호 찾기</a>
                <a href="/sign-up" class="text-[10px] text-white font-normal hover:underline">회원가입</a>
            </div>
        </form>
    </div>

    <!-- Desktop view -->
    <div class="hidden tablet:flex relative h-[calc(100vh-70px)] min-h-[800px] bg-black text-white justify-center">
        <!-- Background image placeholder -->
        <div class="absolute w-full h-full opacity-50 bg-no-repeat bg-cover bg-left-top"
        style="background-image: url('');">
        </div>

        <form onsubmit={handleSubmit} class="flex flex-col justify-between items-center absolute top-[129px] w-[616px] h-[546px] bg-[#252525] rounded-[30px] py-9">

            <!-- Top section -->
            <div class="flex flex-col items-center w-full">
                <h1 class="text-center text-[40px] font-normal mb-14">Login</h1>

                <!-- Error message -->
                {#if error}
                    <div class="mb-6 px-20.5 w-full">
                        <p class="text-red-400 text-center">{error}</p>
                    </div>
                {/if}

                <div class="flex flex-col px-20.5 items-start w-full mb-8 gap-y-3">
                    <label for="tablet-email" class="text-[21px] font-normal">이메일 주소</label>
                    <input
                        id="tablet-email"
                        type="email"
                        bind:value={email}
                        required
                        disabled={isLoading}
                        class="w-full h-[54px] px-5 text-[20px] text-white bg-transparent border-[#AE1F1F] border-[2px] rounded-[50px] focus:outline-none disabled:opacity-50">
                </div>

                <div class="flex flex-col px-20.5 items-start w-full mb-10 gap-y-3">
                    <label for="tablet-password" class="text-[21px] font-normal">비밀번호</label>
                    <input
                        id="tablet-password"
                        type="password"
                        bind:value={password}
                        required
                        disabled={isLoading}
                        class="w-full h-[54px] px-5 text-[20px] text-white bg-transparent border-[#AE1F1F] border-[2px] rounded-[50px] focus:outline-none disabled:opacity-50">
                </div>

                <button
                    type="submit"
                    aria-label="login"
                    disabled={isLoading}
                    class="mb-8.5 bg-[#AE1F1F] w-[122px] h-[47px] rounded-[50px] text-[20px] font-normal font-sogang hover:cursor-pointer hover:bg-[#8a1919] transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                    {isLoading ? '...' : '로그인'}
                </button>
            </div>

            <!-- Bottom links section -->
            <div class="w-full px-22 flex justify-between">
                <a href="/find" class="text-[14px] text-white font-normal hover:underline">비밀번호 찾기</a>
                <a href="/sign-up" class="text-[14px] text-white font-normal hover:underline">회원가입</a>
            </div>
        </form>
        <img alt="SGCC Symbol" src={SGCC_cute} class="absolute top-[65px] w-[166px] left-[calc(50vw-350px)] -rotate-9 mb-4">
    </div>
</main>
