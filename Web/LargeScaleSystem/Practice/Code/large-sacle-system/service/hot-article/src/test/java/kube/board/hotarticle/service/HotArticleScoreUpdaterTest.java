package kube.board.hotarticle.service;

import kube.board.common.event.Event;
import kube.board.hotarticle.repository.ArticleCreatedTimeRepository;
import kube.board.hotarticle.repository.HotArticleListRepository;
import kube.board.hotarticle.service.eventhandler.EventHandler;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.bind.annotation.ModelAttribute;


import java.time.Duration;
import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class HotArticleScoreUpdaterTest {

    @InjectMocks
    HotArticleScoreUpdater hotArticleScoreUpdater;
    @Mock
    HotArticleListRepository hotArticleListRepository;
    @Mock
    HotArticleScoreCalculator hotArticleScoreCalculator;
    @Mock
    ArticleCreatedTimeRepository articleCreatedTimeRepository;

    @Test
    void updateIfArticleNoCreatedTodayTest(){

        // given
        Long articleId = 1L;
        Event event = mock(Event.class);
        EventHandler eventHandler = mock(EventHandler.class);

        given(eventHandler.findArticleId(event)).willReturn(articleId);

        LocalDateTime createdTime = LocalDateTime.now().minusDays(1);
        given(articleCreatedTimeRepository.read(articleId)).willReturn(createdTime);


        // when
        hotArticleScoreUpdater.update(event, eventHandler);

        // then
        verify(eventHandler, never()).handler(event);
        verify(hotArticleListRepository, never())
                .add(anyLong(), any(LocalDateTime.class), anyLong(), anyLong(), any(Duration.class));

    }


    @Test
    void update(){

        // given
        Long articleId = 1L;
        Event event = mock(Event.class);
        EventHandler eventHandler = mock(EventHandler.class);

        given(eventHandler.findArticleId(event)).willReturn(articleId);

        LocalDateTime createdTime = LocalDateTime.now();
        given(articleCreatedTimeRepository.read(articleId)).willReturn(createdTime);


        // when
        hotArticleScoreUpdater.update(event, eventHandler);

        // then
        verify(eventHandler).handler(event);
        verify(hotArticleListRepository)
                .add(anyLong(), any(LocalDateTime.class), anyLong(), anyLong(), any(Duration.class));

    }


}