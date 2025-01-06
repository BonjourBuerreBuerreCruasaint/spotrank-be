useEffect(() => {
  const loadKakaoMap = () => {
    const container = document.getElementById("map"); // 지도를 표시할 HTML 요소
    const options = {
      center: new window.kakao.maps.LatLng(37.5665, 126.9780), // 지도 중심 좌표 (서울)
      level: 3, // 지도 확대 수준
    };

    // 지도 생성
    const map = new window.kakao.maps.Map(container, options);

    // 장소 데이터를 기반으로 마커 추가
    places.forEach((place) => {
      if (!place.latitude || !place.longitude || !place.name) {
        console.warn("유효하지 않은 데이터:", place);
        return;
      }

      const markerPosition = new window.kakao.maps.LatLng(
        place.latitude,
        place.longitude
      );

      // 마커 생성 및 지도에 추가
      const marker = new window.kakao.maps.Marker({
        position: markerPosition,
        map: map,
        title: place.name, // 마커 위에 표시될 이름
      });

      // 정보창 생성
      const infoWindowContent = `
        <div style="padding:10px; font-size:14px;">
          <strong>${place.name}</strong><br />
          위도: ${place.latitude}, 경도: ${place.longitude}
        </div>
      `;
      const infoWindow = new window.kakao.maps.InfoWindow({
        content: infoWindowContent,
      });

      // 마커 클릭 시 정보창 열기/닫기 이벤트 등록
      window.kakao.maps.event.addListener(marker, "click", () => {
        infoWindow.open(map, marker);
      });
    });
  };

  if (window.kakao && window.kakao.maps && places.length > 0) {
    loadKakaoMap(); // 카카오맵 로드 및 마커 추가
  }
}, [places]); // places가 변경될 때마다 실행
