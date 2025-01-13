<template>
  <div class="relative flex items-center ">
    <!-- Info Icon -->
    <div class="relative group ml-auto">
      <!-- Icon -->
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-5 w-5 text-gray-500 cursor-pointer"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        stroke-width="2"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M13 16h-1v-4h-1m1-4h.01M12 20a8 8 0 100-16 8 8 0 000 16z"
        />
      </svg>
      <!-- Tooltip -->
      <div
        class="absolute w-[260px] bottom-full mb-1 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity"
      >
        
Toggle visiblity by clicking on the legends
         <div
          class="absolute top-[17px] left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-800  rotate-45"
        ></div>
      </div>
    </div>
  </div>
</template>

<style>
/* No additional CSS needed with Tailwind */
</style>
