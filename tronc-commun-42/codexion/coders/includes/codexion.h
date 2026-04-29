/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   codexion.h                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: omischle <omischle@student.42.fr>          +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/17 12:00:00 by omischle          #+#    #+#             */
/*   Updated: 2026/04/29 17:03:51 by omischle         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CODEXION_H
# define CODEXION_H

# include <pthread.h>
# include <sys/time.h>
# include <unistd.h>
# include <stdio.h>
# include <stdlib.h>
# include <string.h>

typedef enum e_sched
{
	SCH_FIFO,
	SCH_EDF
}	t_sched;

typedef struct s_request
{
	int		coder_id;
	long	key;
}	t_request;

typedef struct s_pq
{
	t_request	*data;
	int			size;
	int			cap;
	int			(*cmp)(t_request, t_request);
}	t_pq;

typedef struct s_sim	t_sim;

typedef struct s_dongle
{
	int				id;
	int				in_use;
	int				inited;
	long			released_at;
	long			cooldown;
	pthread_mutex_t	lock;
	pthread_cond_t	cond;
	t_pq			waiters;
}	t_dongle;

typedef struct s_coder
{
	int				id;
	int				inited;
	pthread_t		thread;
	int				compiles_done;
	long			last_compile;
	pthread_mutex_t	mtx;
	t_sim			*sim;
}	t_coder;

struct s_sim
{
	int				n;
	long			t_burnout;
	long			t_compile;
	long			t_debug;
	long			t_refactor;
	int				compiles_req;
	long			cooldown;
	t_sched			scheduler;
	long			start_ms;
	int				stop;
	int				n_threads;
	int				mon_created;
	pthread_mutex_t	log_mtx;
	t_dongle		*dongles;
	t_coder			*coders;
	pthread_t		monitor;
};

int			parse_args(t_sim *sim, char **argv);
int			init_sim(t_sim *sim);
void		destroy_sim(t_sim *sim);
void		*coder_routine(void *arg);
void		update_last_compile(t_coder *c);
long		get_last_compile(t_coder *c);
int			get_compiles_done(t_coder *c);
void		inc_compiles_done(t_coder *c);
int			take_dongles(t_coder *c);
void		release_dongles(t_coder *c);
int			acquire_dongle(t_dongle *d, t_coder *c);
void		release_dongle(t_dongle *d);
int			pq_init(t_pq *pq, int cap, int (*c)(t_request, t_request));
void		pq_push(t_pq *pq, t_request req);
t_request	pq_pop(t_pq *pq);
t_request	*pq_peek(t_pq *pq);
void		pq_destroy(t_pq *pq);
void		sift_up(t_pq *pq, int i);
void		sift_down(t_pq *pq, int i);
int			cmp_request(t_request a, t_request b);
void		pq_remove(t_pq *pq, int coder_id);
void		*monitor_routine(void *arg);
long		now_ms(void);
void		precise_sleep(long ms, t_sim *sim);
void		log_state(t_coder *c, const char *msg);
int			sim_stopped(t_sim *sim);

#endif
