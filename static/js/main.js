/**
 * MusicWave - Main JavaScript
 */

$(document).ready(function () {
  // Set up CSRF token for AJAX requests
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie("csrftoken");

  $.ajaxSetup({
    headers: {
      "X-CSRFToken": csrftoken,
    },
  });

  // Global variables
  let audioPlayer = new Audio();
  let currentMusicId = null;
  let isPlaying = false;
  let currentPlaylist = [];
  let currentIndex = 0;

  // Initialize player
  function initPlayer() {
    // Update progress bar while playing
    audioPlayer.addEventListener("timeupdate", updateProgress);

    // When song ends
    audioPlayer.addEventListener("ended", playNext);

    // Set volume
    $("#volume-slider").on("input", function () {
      audioPlayer.volume = $(this).val() / 100;
    });

    // Play/Pause button
    $("#play-btn").on("click", togglePlay);

    // Next button
    $("#next-btn").on("click", playNext);

    // Previous button
    $("#prev-btn").on("click", playPrevious);

    // Close player
    $("#close-player-btn").on("click", closePlayer);

    // Progress bar click
    $(".progress").on("click", function (e) {
      const progressBar = $(this);
      const position = e.pageX - progressBar.offset().left;
      const percent = position / progressBar.width();
      const duration = audioPlayer.duration;

      if (duration) {
        audioPlayer.currentTime = duration * percent;
      }
    });
  }

  // Play music
  function playMusic(id, title, artist, file, cover) {
    // Set current music
    currentMusicId = id;

    // Update player UI
    $("#player-title").text(title);
    $("#player-artist").text(artist);
    $("#player-cover").attr("src", cover || "/static/img/default-cover.jpg");

    // Set audio source
    audioPlayer.src = file;
    audioPlayer.play();

    // Update play button
    $("#play-btn").html('<i class="fas fa-pause"></i>');

    // Show player
    $("#music-player").removeClass("d-none");

    // Update state
    isPlaying = true;

    // Record play if it's a new song
    if (id) {
      $.ajax({
        url: `/music/${id}/play/`,
        type: "POST",
        headers: { "X-CSRFToken": csrftoken },
        success: function (response) {
          console.log("Play recorded");
        },
      });
    }
  }

  // Toggle play/pause
  function togglePlay() {
    if (isPlaying) {
      audioPlayer.pause();
      $("#play-btn").html('<i class="fas fa-play"></i>');
      isPlaying = false;
    } else {
      audioPlayer.play();
      $("#play-btn").html('<i class="fas fa-pause"></i>');
      isPlaying = true;
    }
  }

  // Update progress bar
  function updateProgress() {
    const duration = audioPlayer.duration;
    const currentTime = audioPlayer.currentTime;

    if (duration) {
      // Update progress bar
      const progressPercent = (currentTime / duration) * 100;
      $("#progress-bar").css("width", `${progressPercent}%`);

      // Update time displays
      $("#current-time").text(formatTime(currentTime));
      $("#total-time").text(formatTime(duration));
    }
  }

  // Format time (seconds to MM:SS)
  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds < 10 ? "0" : ""}${remainingSeconds}`;
  }

  // Play next song
  function playNext() {
    if (currentPlaylist.length > 0) {
      currentIndex = (currentIndex + 1) % currentPlaylist.length;
      const nextSong = currentPlaylist[currentIndex];
      playMusic(
        nextSong.id,
        nextSong.title,
        nextSong.artist,
        nextSong.file,
        nextSong.cover
      );
    }
  }

  // Play previous song
  function playPrevious() {
    if (currentPlaylist.length > 0) {
      currentIndex =
        (currentIndex - 1 + currentPlaylist.length) % currentPlaylist.length;
      const prevSong = currentPlaylist[currentIndex];
      playMusic(
        prevSong.id,
        prevSong.title,
        prevSong.artist,
        prevSong.file,
        prevSong.cover
      );
    }
  }

  // Close player
  function closePlayer() {
    audioPlayer.pause();
    $("#music-player").addClass("d-none");
    isPlaying = false;
  }

  // Record play in player
  $("#play-button").on("click", function () {
    const id = $(this).data("music-id");
    const title = $(this).data("music-title");
    const artist = $(this).data("music-artist");
    const file = $(this).data("music-file");
    const cover = $(this).data("music-cover");

    // Set music info to player
    $("#player-title").text(title);
    $("#player-artist").text(artist);
    $("#player-cover").attr("src", cover);

    // Remove setting data-music-id to add-to-playlist-btn

    // Show player
    $("#music-player").removeClass("d-none");

    // Record play
    $.ajax({
      url: `/music/${id}/play/`,
      type: "POST",
      headers: { "X-CSRFToken": csrftoken },
      success: function (response) {
        console.log("Play recorded");
      },
    });

    // Play music
    playMusic(id, title, artist, file, cover);
  });

  // Handle rating stars
  $(document).on("click", ".rating-star", function () {
    const value = $(this).data("value");
    const musicId = $(this).data("music-id");

    // Update UI
    $(".rating-star").removeClass("active");
    $(this).prevAll(".rating-star").addBack().addClass("active");

    // Submit rating
    $.ajax({
      url: `/music/${musicId}/rate/`,
      type: "POST",
      headers: { "X-CSRFToken": csrftoken },
      data: {
        rating: value,
        liked: value >= 4, // Like if rating is 4 or 5
      },
      success: function (response) {
        console.log("Rating submitted");
      },
    });
  });

  // Initialize the player
  initPlayer();

  // Global handler for all play buttons across the site
  $(document).on("click", ".play-btn", function () {
    const musicId = $(this).data("music-id");
    const musicTitle = $(this).data("music-title");
    const musicArtist = $(this).data("music-artist");
    const musicFile = $(this).data("music-file");
    const musicCover = $(this).data("music-cover");

    // Add song to playlist
    currentPlaylist = [
      {
        id: musicId,
        title: musicTitle,
        artist: musicArtist,
        file: musicFile,
        cover: musicCover,
      },
    ];
    currentIndex = 0;

    // Play the music
    playMusic(musicId, musicTitle, musicArtist, musicFile, musicCover);
  });

  // Play all button handler
  $(document).on("click", ".play-all-btn", function () {
    // Build playlist from all visible play buttons
    currentPlaylist = [];
    $(".play-btn").each(function () {
      currentPlaylist.push({
        id: $(this).data("music-id"),
        title: $(this).data("music-title"),
        artist: $(this).data("music-artist"),
        file: $(this).data("music-file"),
        cover: $(this).data("music-cover"),
      });
    });

    // Play the first song if playlist is not empty
    if (currentPlaylist.length > 0) {
      currentIndex = 0;
      const firstSong = currentPlaylist[0];
      playMusic(
        firstSong.id,
        firstSong.title,
        firstSong.artist,
        firstSong.file,
        firstSong.cover
      );
    }
  });

  // Initialize tooltips
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Add to playlist button click handler - removed

  // Function to load user playlists - removed

  // Add to playlist form submission - removed

  // Handle playlist edit button click (global handler)
  $(document).on("click", ".edit-playlist-btn", function () {
    const playlistId = $(this).data("playlist-id");

    // Set the form action URL
    $("#edit-playlist-form").attr("action", `/playlists/${playlistId}/edit/`);

    // Reset form fields
    $("#edit-playlist-form")[0].reset();
    $(".current-cover").addClass("d-none");
    $(".alert").remove(); // Remove any previous alerts

    // Show loading state
    $(".modal-body").append(
      '<div class="text-center my-3 loading-spinner"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>'
    );

    // Load playlist data
    $.ajax({
      url: `/playlists/${playlistId}/edit/`,
      type: "GET",
      success: function (response) {
        // Remove loading spinner
        $(".loading-spinner").remove();

        // Fill form fields with playlist data
        $("#edit-name").val(response.playlist.name);
        $("#edit-description").val(response.playlist.description);
        $("#edit-is-public").prop("checked", response.playlist.is_public);

        // Show current cover image if exists
        if (response.playlist.cover_image) {
          $(".current-cover").removeClass("d-none");
          $("#current-cover-preview").attr(
            "src",
            response.playlist.cover_image
          );
          $("#current-cover-preview").attr("alt", response.playlist.name);
        }
      },
      error: function () {
        // Remove loading spinner
        $(".loading-spinner").remove();

        // Show error message
        $(".modal-body").prepend(`
          <div class="alert alert-danger" style="color: black;">
            Failed to load playlist data. Please try again.
          </div>
        `);
      },
    });
  });

  // Handle playlist edit form submission
  $(document).on("submit", "#edit-playlist-form", function () {
    // Show loading state on button
    const submitBtn = $(this).find('button[type="submit"]');
    const originalText = submitBtn.text();
    submitBtn.html(
      '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Saving...'
    );
    submitBtn.prop("disabled", true);

    // Form will submit normally, this just shows the loading state
  });

  // Handle Add to Playlist button click
  $(document).on("click", ".add-to-playlist-btn", function () {
    const musicId = $(this).data("music-id");
    $("#music_id").val(musicId);

    // Clear previous content
    $("#playlists-container").html(
      '<div class="text-center py-3"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Loading your playlists...</p></div>'
    );

    // Load user playlists
    loadUserPlaylists();
  });

  // Function to load user playlists
  function loadUserPlaylists() {
    $.ajax({
      url: "/api/playlists/",
      type: "GET",
      success: function (response) {
        if (response.success) {
          renderPlaylists(response.playlists);
        } else {
          $("#playlists-container").html(
            '<div class="alert alert-danger">Failed to load playlists</div>'
          );
        }
      },
      error: function () {
        $("#playlists-container").html(
          '<div class="alert alert-danger">Failed to load playlists</div>'
        );
      },
    });
  }

  // Render playlists in the modal
  function renderPlaylists(playlists) {
    if (playlists.length === 0) {
      $("#playlists-container").html(
        '<div class="alert alert-info" style="color: black;">You don\'t have any playlists yet. Create a new one below.</div>'
      );
      return;
    }

    let html = '<div class="playlists-grid">';

    playlists.forEach(function (playlist) {
      html += `
        <div class="playlist-item">
          <input type="radio" class="playlist-radio" name="playlist_id" id="playlist-${
            playlist.id
          }" value="${playlist.id}">
          <label class="playlist-label" for="playlist-${playlist.id}">
            <div class="playlist-cover">
              ${
                playlist.cover_image
                  ? `<img src="${playlist.cover_image}" alt="${playlist.name}">`
                  : '<div class="default-cover"><i class="fas fa-music"></i></div>'
              }
            </div>
            <div class="playlist-info">
              <h5 style="color: black;">${playlist.name}</h5>
              <small style="color: black;">${playlist.item_count} songs</small>
            </div>
          </label>
        </div>
      `;
    });

    html += "</div>";
    $("#playlists-container").html(html);
  }

  // Handle Add to Playlist form submission
  $(document).on("submit", "#add-to-playlist-form", function (e) {
    e.preventDefault();

    const musicId = $("#music_id").val();
    const playlistId = $("input[name='playlist_id']:checked").val();
    const newPlaylistName = $("#new-playlist-name").val();
    const newPlaylistPublic = $("#new-playlist-public").is(":checked");

    // Show loading state
    const submitBtn = $(this).find('button[type="submit"]');
    const originalText = submitBtn.text();
    submitBtn.html(
      '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Adding...'
    );
    submitBtn.prop("disabled", true);

    // Prepare form data
    let formData = new FormData();
    formData.append("music_id", musicId);

    if (playlistId) {
      formData.append("playlist_id", playlistId);
    } else if (newPlaylistName) {
      formData.append("new_playlist_name", newPlaylistName);
      formData.append("new_playlist_public", newPlaylistPublic ? "on" : "off");
    } else {
      // Show error if neither option is selected
      $("#add-to-playlist-modal-footer").prepend(
        '<div class="alert alert-danger">Please select a playlist or create a new one</div>'
      );
      submitBtn.html(originalText);
      submitBtn.prop("disabled", false);
      return;
    }

    // Submit form
    $.ajax({
      url: "/add-to-playlist/",
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
      success: function (response) {
        if (response.success) {
          // Show success message
          $("#add-to-playlist-modal").modal("hide");

          // Show toast notification
          const toast = `
            <div class="toast align-items-center text-white bg-success border-0 position-fixed bottom-0 end-0 m-3" role="alert" aria-live="assertive" aria-atomic="true">
              <div class="d-flex">
                <div class="toast-body">
                  <i class="fas fa-check-circle me-2"></i> ${response.message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
              </div>
            </div>
          `;

          $("body").append(toast);
          const toastElement = $(".toast").last();
          const bsToast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 3000,
          });
          bsToast.show();

          // Remove toast after it's hidden
          toastElement.on("hidden.bs.toast", function () {
            $(this).remove();
          });
        } else {
          // Show error message
          $("#add-to-playlist-modal-footer").prepend(
            `<div class="alert alert-danger">${
              response.message || "Failed to add to playlist"
            }</div>`
          );
        }
      },
      error: function () {
        // Show error message
        $("#add-to-playlist-modal-footer").prepend(
          '<div class="alert alert-danger">An error occurred. Please try again.</div>'
        );
      },
      complete: function () {
        // Reset button state
        submitBtn.html(originalText);
        submitBtn.prop("disabled", false);

        // Reset form
        $("#add-to-playlist-form")[0].reset();
        $(".alert").remove();
      },
    });
  });
});
